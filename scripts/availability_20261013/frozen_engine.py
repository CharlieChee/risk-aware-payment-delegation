"""Deterministic, finite-catalog RAC experiment engine. No orders are executed.

Public API
==========
``evaluate(expr, attrs)`` returns ``bool``, ``fractions.Fraction``, or ``None``
(unknown). Invalid syntax/types raise ``DSLValidationError``. ``solve`` turns
invalid input into a fail-closed ``invalid_spec`` result.

Expressions are interpreted from a validated Python AST; Python code execution
is never used. Supported syntax: numeric/Boolean literals, variable names,
and/or/not, comparisons, + - * /, conditional expressions, min/max/abs.
Numeric literals and decimal-string attributes are exact. Boolean values are
not coerced to numbers or vice versa. Missing/null attributes and division by
zero are unknown. Unknown Boolean operations use strong Kleene logic. An
unknown conditional has a known result only if both branches have the same
known value and type. Unknown utility cannot certify a utility-based choice.

Limits: 200,000 characters, 100,000 AST nodes, and AST depth 100 per expression;
256 characters per numeric string/literal; decimal exponent magnitude at most 1,000;
4,096 bits each for every rational numerator/denominator; 256 states; 10,000
candidates; 1,024 attributes per candidate; 1,000,000 state/candidate pairs;
up to 4,096 positional arguments to min/max (abs still takes exactly one).
Resource-limit violations are invalid input, never approximate computation.

``full`` maximizes minimum utility over candidates whose hard and risk
predicates are True in every state. ``single_state`` keeps only the first
state; ``no_risk`` ignores risk predicates for eligibility; ``no_utility``
permits every certified-safe candidate, including nonpositive/unknown utility
(an explicitly marked ablation). The first three modes prefer rejection on a
utility tie. A utility_floor above rejection utility instead admits every safe
candidate with a known minimum utility at least that floor. It is incompatible
with no_utility. Floor inputs can be Fraction, int, or decimal/rational string;
floating-point inputs are rejected. reject_utility is a decimal/rational string.

All optimality claims concern certified *observed* candidates. A complete
catalog is asserted by the caller, not verified here. Rejections return no
allowed ids and guaranteed_utility=None; rejection utility is reported
separately. In floor/no_utility mode an accepted set's guaranteed utility is its
lowest known minimum utility, or None if the ablation permits unknown utility.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Any


MAX_EXPR_CHARS = 200_000
MAX_AST_NODES = 100_000
MAX_AST_DEPTH = 100
MAX_NUMBER_CHARS = 256
MAX_DECIMAL_EXPONENT = 1_000
MAX_RATIONAL_BITS = 4_096
MAX_STATES = 256
MAX_CANDIDATES = 10_000
MAX_ATTRIBUTES = 1_024
MAX_STATE_CANDIDATE_PAIRS = 1_000_000
MAX_IDENTIFIER_CHARS = 128
MAX_CALL_ARGUMENTS = 4_096

Value = bool | Fraction | None
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_RATIONAL = re.compile(r"[+-]?[0-9]+/[+-]?[0-9]+\Z")
_MODES = {"full", "single_state", "no_risk", "no_utility"}
_CALLS = {"min", "max", "abs"}
_ALLOWED_NODES = {
    ast.Expression, ast.Constant, ast.Name, ast.Load, ast.BoolOp, ast.And,
    ast.Or, ast.UnaryOp, ast.Not, ast.UAdd, ast.USub, ast.BinOp, ast.Add,
    ast.Sub, ast.Mult, ast.Div, ast.Compare, ast.Eq, ast.NotEq, ast.Lt,
    ast.LtE, ast.Gt, ast.GtE, ast.IfExp, ast.Call,
}


class DSLValidationError(ValueError):
    """The expression, schema, type, or resource bound is invalid."""


@dataclass(frozen=True)
class _Program:
    root: ast.expr
    constants: dict[ast.Constant, Value]
    variables: frozenset[str]


def _bounded(value: Fraction) -> Fraction:
    if (value.numerator.bit_length() > MAX_RATIONAL_BITS
            or value.denominator.bit_length() > MAX_RATIONAL_BITS):
        raise DSLValidationError("rational exceeds the 4096-bit numerator/denominator limit")
    return value


def _number_text(value: str, *, allow_rational: bool = False) -> Fraction:
    if len(value) > MAX_NUMBER_CHARS:
        raise DSLValidationError("numeric input exceeds 256 characters")
    value = value.strip()
    decimal = _DECIMAL.fullmatch(value)
    rational = allow_rational and _RATIONAL.fullmatch(value)
    if not decimal and not rational:
        raise DSLValidationError("expected a finite decimal" + (" or rational" if allow_rational else "") + " string")
    if decimal and "e" in value.lower():
        exponent = int(value.lower().split("e")[1])
        if abs(exponent) > MAX_DECIMAL_EXPONENT:
            raise DSLValidationError("decimal exponent magnitude exceeds 1000")
    try:
        return _bounded(Fraction(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise DSLValidationError("invalid finite numeric input") from exc


def _valid_name(name: str) -> bool:
    return (isinstance(name, str) and len(name) <= MAX_IDENTIFIER_CHARS
            and name.isidentifier() and not name.startswith("__"))


def _attrs(attrs: dict[str, Any]) -> dict[str, Value]:
    if not isinstance(attrs, dict) or len(attrs) > MAX_ATTRIBUTES:
        raise DSLValidationError("attrs must be an object with at most 1024 attributes")
    result: dict[str, Value] = {}
    for key, value in attrs.items():
        if not _valid_name(key):
            raise DSLValidationError("attribute keys must be ordinary variable identifiers")
        if value is None or type(value) is bool:
            result[key] = value
        elif type(value) is int:
            result[key] = _bounded(Fraction(value))
        elif type(value) is str:
            result[key] = _number_text(value)
        else:
            raise DSLValidationError("attribute values must be bool, int, decimal-string, or null")
    return result


def _compile(expr: str) -> _Program:
    if not isinstance(expr, str) or not expr.strip():
        raise DSLValidationError("expression must be a nonempty string")
    if len(expr) > MAX_EXPR_CHARS:
        raise DSLValidationError("expression exceeds 200000 characters")
    return _compile_cached(expr)


@lru_cache(maxsize=512)
def _compile_cached(expr: str) -> _Program:
    source = expr.strip()
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise DSLValidationError("invalid expression syntax") from exc
    constants: dict[ast.Constant, Value] = {}
    names: set[str] = set()
    stack: list[tuple[ast.AST, int, ast.AST | None]] = [(tree, 0, None)]
    count = 0
    while stack:
        node, depth, parent = stack.pop()
        count += 1
        if count > MAX_AST_NODES:
            raise DSLValidationError("expression exceeds 100000 AST nodes")
        if depth > MAX_AST_DEPTH:
            raise DSLValidationError("expression exceeds AST depth 100")
        if type(node) not in _ALLOWED_NODES:
            raise DSLValidationError("unsupported DSL syntax: " + type(node).__name__)
        if isinstance(node, ast.Constant):
            if type(node.value) is bool:
                constants[node] = node.value
            elif type(node.value) is int:
                literal = ast.get_source_segment(source, node)
                if literal is None or len(literal.replace("_", "")) > MAX_NUMBER_CHARS:
                    raise DSLValidationError("numeric literal exceeds 256 characters")
                constants[node] = _bounded(Fraction(node.value))
            elif type(node.value) is float:
                # Reparse the source lexeme, never the rounded Python float.
                literal = ast.get_source_segment(source, node)
                if literal is None:
                    raise DSLValidationError("numeric literal has no source text")
                constants[node] = _number_text(literal.replace("_", ""))
            else:
                raise DSLValidationError("only numeric and Boolean literals are supported")
        elif isinstance(node, ast.Name):
            if not _valid_name(node.id):
                raise DSLValidationError("invalid variable name")
            if not (isinstance(parent, ast.Call) and parent.func is node):
                names.add(node.id)
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _CALLS:
                raise DSLValidationError("only min/max/abs calls are supported")
            if node.keywords or not 1 <= len(node.args) <= MAX_CALL_ARGUMENTS:
                raise DSLValidationError("calls require 1 to 4096 positional arguments")
            if node.func.id == "abs" and len(node.args) != 1:
                raise DSLValidationError("abs requires exactly one argument")
        stack.extend((child, depth + 1, node) for child in ast.iter_child_nodes(node))
    return _Program(tree.body, constants, frozenset(names))


def _boolean(value: Value) -> bool | None:
    if value is None or type(value) is bool:
        return value
    raise DSLValidationError("Boolean context requires a bool, not a number")


def _numeric(value: Value) -> Fraction | None:
    if value is None or isinstance(value, Fraction):
        return value
    raise DSLValidationError("numeric context requires a number, not a bool")


def _comparison(op: ast.cmpop, left: Value, right: Value) -> bool | None:
    if left is None or right is None:
        return None
    equality = isinstance(op, (ast.Eq, ast.NotEq))
    if type(left) is not type(right):
        raise DSLValidationError("comparison operands must have the same type")
    if type(left) is bool and not equality:
        raise DSLValidationError("Boolean values support only == and != comparisons")
    if isinstance(op, ast.Eq):
        return left == right
    if isinstance(op, ast.NotEq):
        return left != right
    if isinstance(op, ast.Lt):
        return left < right
    if isinstance(op, ast.LtE):
        return left <= right
    if isinstance(op, ast.Gt):
        return left > right
    if isinstance(op, ast.GtE):
        return left >= right
    raise DSLValidationError("unsupported comparison")


def _run(program: _Program, attrs: dict[str, Value]) -> Value:
    def visit(node: ast.expr) -> Value:
        if isinstance(node, ast.Constant):
            return program.constants[node]
        if isinstance(node, ast.Name):
            return attrs.get(node.id)
        if isinstance(node, ast.BoolOp):
            unknown = False
            conjunction = isinstance(node.op, ast.And)
            for operand in node.values:
                value = _boolean(visit(operand))
                if value is None:
                    unknown = True
                elif conjunction and value is False:
                    return False
                elif not conjunction and value is True:
                    return True
            return None if unknown else conjunction
        if isinstance(node, ast.UnaryOp):
            value = visit(node.operand)
            if isinstance(node.op, ast.Not):
                boolean = _boolean(value)
                return None if boolean is None else not boolean
            numeric = _numeric(value)
            if numeric is None:
                return None
            return _bounded(-numeric if isinstance(node.op, ast.USub) else numeric)
        if isinstance(node, ast.BinOp):
            left, right = _numeric(visit(node.left)), _numeric(visit(node.right))
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return _bounded(left + right)
            if isinstance(node.op, ast.Sub):
                return _bounded(left - right)
            if isinstance(node.op, ast.Mult):
                return _bounded(left * right)
            if isinstance(node.op, ast.Div):
                return None if right == 0 else _bounded(left / right)
        if isinstance(node, ast.Compare):
            left = visit(node.left)
            unknown = False
            for op, operand in zip(node.ops, node.comparators):
                right = visit(operand)
                value = _comparison(op, left, right)
                if value is False:
                    return False
                unknown |= value is None
                left = right
            return None if unknown else True
        if isinstance(node, ast.IfExp):
            condition = _boolean(visit(node.test))
            if condition is not None:
                return visit(node.body if condition else node.orelse)
            left, right = visit(node.body), visit(node.orelse)
            return left if left is not None and type(left) is type(right) and left == right else None
        if isinstance(node, ast.Call):
            values = [_numeric(visit(arg)) for arg in node.args]
            if any(value is None for value in values):
                return None
            # The validator restricts the callable name and argument count.
            if node.func.id == "min":
                return min(values)
            if node.func.id == "max":
                return max(values)
            return _bounded(abs(values[0]))
        raise DSLValidationError("unsupported executable AST node")

    return visit(program.root)


def evaluate(expr: str, attrs: dict[str, Any]) -> Value:
    """Interpret a validated expression, returning bool/Fraction/unknown(None)."""
    return _run(_compile(expr), _attrs(attrs))


def _floor(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return _bounded(value)
    if type(value) is int:
        return _bounded(Fraction(value))
    if type(value) is str:
        return _number_text(value, allow_rational=True)
    raise DSLValidationError("utility_floor must be a Fraction, int, or exact numeric string")


def solve(spec: dict[str, Any], candidates: list[dict[str, Any]],
          mode: str = "full", utility_floor: Any = None) -> dict[str, Any]:
    """Return the certified observed candidate set, or a conservative rejection.

    Schema: spec={states:[{label,hard,risk,utility}],reject_utility:str,
    catalog_complete:bool,source_ids:[str]}; candidates=[{id:str,attrs:{...}}].
    Candidate IDs and state labels must be nonempty and unique. Syntax in all
    states is checked even when single_state retains only the first state.
    The matrix contains retained states only; safe excludes utility, and psi
    is present iff every retained state's utility is known.
    """
    matrix: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "decision": "reject", "allowed_ids": [], "guaranteed_utility": None,
        "reason_code": "invalid_spec", "matrix": matrix,
        "no_orders_executed": True,
        "optimization_scope": "certified_observed_candidates",
    }
    try:
        if not isinstance(spec, dict):
            raise DSLValidationError("spec must be an object")
        required = {"states", "reject_utility", "catalog_complete", "source_ids"}
        if not required.issubset(spec):
            raise DSLValidationError("spec is missing required fields")
        if not isinstance(mode, str) or mode not in _MODES:
            raise DSLValidationError("unsupported mode")
        result["mode"] = mode
        if type(spec["catalog_complete"]) is not bool:
            raise DSLValidationError("catalog_complete must be a Boolean")
        complete = spec["catalog_complete"]
        result["catalog_complete"] = complete
        if not isinstance(spec["source_ids"], list) or any(
                not isinstance(value, str) for value in spec["source_ids"]):
            raise DSLValidationError("source_ids must be an array of strings")
        if type(spec["reject_utility"]) is not str:
            raise DSLValidationError("reject_utility must be an exact numeric string")
        reject = _number_text(spec["reject_utility"], allow_rational=True)
        result["reject_utility"] = str(reject)
        floor = None if utility_floor is None else _floor(utility_floor)
        if floor is not None and floor <= reject:
            raise DSLValidationError("utility_floor must be strictly above reject_utility")
        if floor is not None and mode == "no_utility":
            raise DSLValidationError("utility_floor is incompatible with no_utility")
        result["utility_floor"] = None if floor is None else str(floor)
        states = spec["states"]
        if not isinstance(states, list) or not 1 <= len(states) <= MAX_STATES:
            raise DSLValidationError("states must contain 1 to 256 states")
        programs: list[tuple[str, _Program, _Program, _Program]] = []
        labels: set[str] = set()
        for state in states:
            if not isinstance(state, dict) or not {"label", "hard", "risk", "utility"}.issubset(state):
                raise DSLValidationError("each state requires label, hard, risk, and utility")
            label = state["label"]
            if not isinstance(label, str) or not label or label in labels:
                raise DSLValidationError("state labels must be unique nonempty strings")
            labels.add(label)
            programs.append((label, _compile(state["hard"]), _compile(state["risk"]), _compile(state["utility"])))
        if mode == "single_state":
            programs = programs[:1]
        result["retained_states"] = [entry[0] for entry in programs]
        if not isinstance(candidates, list) or len(candidates) > MAX_CANDIDATES:
            raise DSLValidationError("candidates must be an array of at most 10000 items")
        if len(programs) * len(candidates) > MAX_STATE_CANDIDATE_PAIRS:
            raise DSLValidationError("state/candidate pair limit exceeded")
        normalized: list[tuple[str, dict[str, Value]]] = []
        ids: set[str] = set()
        for candidate in candidates:
            if not isinstance(candidate, dict) or not {"id", "attrs"}.issubset(candidate):
                raise DSLValidationError("each candidate requires id and attrs")
            identity = candidate["id"]
            if not isinstance(identity, str) or not identity or identity in ids:
                raise DSLValidationError("candidate ids must be unique nonempty strings")
            ids.add(identity)
            normalized.append((identity, _attrs(candidate["attrs"])))

        scored: list[tuple[dict[str, Any], Fraction | None, bool]] = []
        for identity, attrs in normalized:
            state_values: list[dict[str, Any]] = []
            predicates: list[bool | None] = []
            utilities: list[Fraction | None] = []
            missing: set[str] = set()
            for label, hard_program, risk_program, utility_program in programs:
                hard = _boolean(_run(hard_program, attrs))
                risk = _boolean(_run(risk_program, attrs))
                utility = _numeric(_run(utility_program, attrs))
                state_values.append({"label": label, "hard": hard, "risk": risk,
                                     "utility": None if utility is None else str(utility)})
                predicates.append(hard)
                if mode != "no_risk":
                    predicates.append(risk)
                utilities.append(utility)
                for program in (hard_program, risk_program, utility_program):
                    missing.update(name for name in program.variables if attrs.get(name) is None)
            safe = all(value is True for value in predicates)
            proven_unsafe = any(value is False for value in predicates)
            psi = None if any(value is None for value in utilities) else min(utilities)
            if proven_unsafe:
                detail = "required_predicate_false"
            elif not safe:
                detail = "required_predicate_unknown"
            elif psi is None:
                detail = "utility_unknown"
            elif psi <= reject:
                detail = "utility_not_above_rejection"
            elif floor is not None and psi < floor:
                detail = "utility_below_floor"
            else:
                detail = "certified_eligible"
            row = {"id": identity, "states": state_values, "safe": safe,
                   "psi": None if psi is None else str(psi),
                   "proven_unsafe": proven_unsafe, "evidence_code": detail,
                   "missing_attributes": sorted(missing)}
            matrix.append(row)
            scored.append((row, psi, proven_unsafe))

        safe_rows = [entry for entry in scored if entry[0]["safe"]]
        if mode == "no_utility":
            allowed = safe_rows
        else:
            eligible = [entry for entry in safe_rows if entry[1] is not None
                        and entry[1] > reject and (floor is None or entry[1] >= floor)]
            if floor is not None:
                allowed = eligible
            elif eligible:
                best = max(entry[1] for entry in eligible)
                allowed = [entry for entry in eligible if entry[1] == best]
            else:
                allowed = []
        result["optimization_applied"] = mode != "no_utility" and floor is None
        if allowed:
            guarantee = (None if any(entry[1] is None for entry in allowed)
                         else str(min(entry[1] for entry in allowed)))
            result.update(decision="accept", allowed_ids=[entry[0]["id"] for entry in allowed],
                          guaranteed_utility=guarantee, reason_code="optimal_certified")
            if mode == "no_utility":
                result["detail"] = "ablation_all_certified_safe_candidates"
            elif floor is not None:
                result["detail"] = "all_certified_candidates_meeting_utility_floor"
            else:
                result["detail"] = "all_maximin_ties_among_certified_observed_candidates"
            return result

        unresolved = any(not proven_unsafe and
                         (not row["safe"] or (mode != "no_utility" and psi is None))
                         for row, psi, proven_unsafe in scored)
        if not complete:
            reason, detail = "no_certified_observed_candidate", "catalog_is_incomplete"
        elif unresolved:
            reason, detail = "no_certified_observed_candidate", "relevant_evidence_is_unknown"
        elif not safe_rows:
            reason, detail = "infeasible_complete_catalog", "every_catalog_candidate_is_proven_unsafe_or_catalog_is_empty"
        elif all(entry[1] <= reject for entry in safe_rows):
            reason, detail = "utility_not_positive", "all_certified_safe_utilities_are_at_or_below_rejection"
        else:
            reason, detail = "no_certified_observed_candidate", "no_observed_candidate_meets_utility_floor"
        result.update(reason_code=reason, detail=detail)
        return result
    except (DSLValidationError, RecursionError) as exc:
        # Do not retain partial candidate evidence from an invalid evaluation.
        result.update(decision="reject", allowed_ids=[], guaranteed_utility=None,
                      reason_code="invalid_spec", matrix=[], detail=str(exc))
        return result
