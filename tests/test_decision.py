import unittest
from risk_payment.decision import decide, score
from risk_payment.engine import evaluate, DSLValidationError

def spec(hard='True', risk='True', utility='value'):
    return dict(states=[dict(label='s',hard=hard,risk=risk,utility=utility)],
                source_ids=[],reject_utility='0',catalog_complete=True)

def candidate(identity,**attrs):return dict(id=identity,attrs=attrs)

class DecisionTests(unittest.TestCase):
    def test_unknown_better_competitor_prevents_claim_of_optimality(self):
        r=decide(spec(),[candidate('A',value=10),candidate('B',value=None)])
        self.assertEqual(r['status'],'failure')

    def test_irrelevant_unknown_does_not_block_a_known_optimum(self):
        r=decide(spec(hard='eligible'),[candidate('A',eligible=True,value=10),candidate('B',eligible=False,value=None)])
        self.assertEqual(r['allowed_ids'],['A'])

    def test_complete_infeasibility_and_nonpositive_value_are_distinct(self):
        self.assertEqual(decide(spec(hard='False'),[candidate('A',value=None)])['reason'],'infeasible')
        self.assertEqual(decide(spec(),[candidate('A',value=0)])['reason'],'nonpositive_value')

    def test_joint_action_and_worst_case_ranking(self):
        q=spec(utility='u1');q['states'].append(dict(label='other',hard='True',risk='True',utility='u2'))
        r=decide(q,[candidate('A',u1=100,u2=1),candidate('B',u1=10,u2=10)])
        self.assertEqual(r['allowed_ids'],['B'])

    def test_exact_decimal_boundary(self):
        self.assertTrue(evaluate('0.1 + 0.2 == 0.3',{}))
        self.assertFalse(evaluate('loss <= cap',{'loss':200001,'cap':200000}))

    def test_expression_language_cannot_execute_code(self):
        with self.assertRaises(DSLValidationError):evaluate('__import__("os").system("true")',{})
        with self.assertRaises(DSLValidationError):evaluate('True + 1',{})

    def test_incomplete_catalogue_is_failure_not_certified_refusal(self):
        self.assertEqual(decide(spec(),[],False)['status'],'failure')

    def test_multiple_optima_and_safe_nonoptimal_output(self):
        ref=dict(decision='accept',allowed_ids=['A','B'],guaranteed_utility='10',
                 matrix=[dict(id='A',safe=True),dict(id='B',safe=True),dict(id='C',safe=True)])
        self.assertTrue(score(dict(decision='accept',allowed_ids=['B'],guaranteed_utility='10'),ref)['exact'])
        self.assertTrue(score(dict(decision='accept',allowed_ids=['C'],guaranteed_utility='1'),ref)['other'])

if __name__=='__main__':unittest.main()
