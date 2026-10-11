from pathlib import Path
from types import SimpleNamespace
import json, tempfile, unittest
from risk_payment.run import one, save, decode
from risk_payment.prompts import request, SCHEMAS

class RunnerTests(unittest.TestCase):
    def test_carrier_decoding_cannot_choose_between_competing_answers(self):
        answer=dict(decision='reject',allowed_ids=[],guaranteed_utility=None,reason='No candidate.')
        payload=json.dumps(SCHEMAS['direct'])+'\n'+json.dumps(answer)
        parsed,trace=decode(payload)
        self.assertEqual(parsed,answer)
        self.assertFalse(trace['expressions_edited'])
        alternate=dict(answer,decision='accept',allowed_ids=['A'],guaranteed_utility='10')
        with self.assertRaises(ValueError):decode(json.dumps(answer)+'\n'+json.dumps(alternate))

    def test_catalogue_and_reference_are_not_in_compilation_messages(self):
        body=json.loads(request('set',dict(records=[],attributes={'price':'price'},candidates=[{'id':'secret_catalogue_id'}],catalog_complete=True))[1]['content'])
        self.assertNotIn('candidates',body)
        self.assertNotIn('reference',body)

    def test_saved_response_is_reused_after_scoring_interruption(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);public=dict(records=[],attributes={},candidates=[],catalog_complete=True)
            save(root/'public.json',public)
            save(root/'ref.json',{'reference':dict(decision='reject',allowed_ids=[],guaranteed_utility=None,matrix=[])})
            args=SimpleNamespace(benchmark=root,model='mock',method='direct',output_cap=100,effort=None,
                 temperature=None,json_mode=False,output=root/'results',base_url='https://example.invalid/v1',timeout=1)
            case={'id':'case','public_path':'public.json','reference_path':'ref.json'}
            calls=[]
            def transport(*unused):
                calls.append(1)
                return {'model':'mock','choices':[{'message':{'content':json.dumps(dict(decision='reject',allowed_ids=[],guaranteed_utility=None,reason='No candidate.'))}}],'usage':{'total_tokens':7}}
            first=one(args,case,'not-a-real-key',transport)
            (args.output/'case/result.json').unlink()
            second=one(args,case,'not-a-real-key',transport)
            self.assertEqual(len(calls),1)
            self.assertEqual(first,second)
            self.assertTrue(second['metrics']['exact'])
            self.assertNotIn('not-a-real-key',(args.output/'case/request.json').read_text())
            args.output_cap=200
            with self.assertRaises(ValueError):one(args,case,'not-a-real-key',transport)

if __name__=='__main__':unittest.main()
