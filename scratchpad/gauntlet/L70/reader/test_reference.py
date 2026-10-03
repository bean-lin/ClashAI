"""Offline checks with captured Rocket/evolution evidence and malformed controls."""
import json
from pathlib import Path
import struct
import unittest
from probe_host import parse_peek
from reference_fields import Memory,MissingRead,decode_object,decode,evo,AREA_VT
from build_source import generate,SOURCE,HERE

class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frames={}
        with (HERE/'capture_a.jsonl').open() as f:
            for line in f:
                row=json.loads(line)
                if row['event']=='meta': cls.base=row['libg_base']
                elif row['seq'] in (105,106): cls.frames[row['seq']]=row
    def memory(self,seq):
        return Memory((a,n,bytes.fromhex(h) if h is not None else None,e)
                      for a,n,h,e in self.frames[seq]['blocks'])
    def test_rocket_matches_confirmed_target_and_moves_toward_it(self):
        a=0x74b519d47a00
        _,p=decode_object(self.memory(105),self.base,a)
        _,q=decode_object(self.memory(106),self.base,a)
        self.assertEqual((p['card_id'],p['side'],p['target_x'],p['target_y']),(28000003,1,13500,7500))
        self.assertEqual((p['x'],p['y'],q['x'],q['y']),(11640,16346,13078,9506))
        distance=lambda o:(o['x']-o['target_x'])**2+(o['y']-o['target_y'])**2
        self.assertLess(distance(q),distance(p))
    def test_wrong_vtable_cannot_be_classified_as_projectile(self):
        a=0x74b519d47a00; raw=bytearray(self.memory(105).read(a,0x128))
        struct.pack_into('<Q',raw,0,self.base+0x1969b38) # other-build vtable
        kind,obj=decode_object(Memory([(a,len(raw),bytes(raw),None)]),self.base,a)
        self.assertEqual(kind,'unknown_nonunits')
    def test_parse_errors_are_explicit(self):
        self.assertEqual(parse_peek('0x10000 4 ERR 5\n'),[(0x10000,4,None,5)])
        self.assertRaises(ValueError,parse_peek,'0x10000 4 0102\n')
        self.assertRaises(MissingRead,Memory([(0x10000,4,None,5)]).read,0x10000,4)
        decoded=decode([],self.base)
        self.assertFalse(decoded['extension']['valid'])
        self.assertGreater(decoded['extension']['read_errors'],0)
    def test_effect_countdown_and_negative_unknown(self):
        a=0x10000; data=0x20000; raw=bytearray(0x128)
        struct.pack_into('<Q',raw,0,self.base+AREA_VT)
        struct.pack_into('<i',raw,8,3000001); struct.pack_into('<Q',raw,0x48,data)
        struct.pack_into('<i',raw,0x100,300); struct.pack_into('<i',raw,0x114,-1)
        def value():
            m=Memory([(a,len(raw),bytes(raw),None)])
            return decode_object(m,self.base,a)[1]['remaining_ms']
        self.assertEqual(value(),300)
        struct.pack_into('<i',raw,0x100,-1)
        self.assertIsNone(value())
        struct.pack_into('<i',raw,0x100,0)
        self.assertEqual(value(),0)
    def test_recorded_tornado_stays_at_target_and_counts_down(self):
        result=[]
        with (HERE/'capture_b.jsonl').open() as f:
            for line in f:
                row=json.loads(line)
                if row['event']!='batch' or row['seq'] not in (323,324): continue
                m=Memory((a,n,bytes.fromhex(h) if h is not None else None,e) for a,n,h,e in row['blocks'])
                key,obj=decode_object(m,self.base,0x74b4780ffad0)
                self.assertEqual(key,'effects')
                self.assertEqual((obj['card_id'],obj['side'],obj['x'],obj['y']),(28000012,1,4500,17500))
                result.append(obj['remaining_ms'])
        self.assertEqual(result,[400,50])
    def test_evo_boundary_and_real_body_names_cycles(self):
        self.assertEqual([evo(x) for x in (-1,12999999,13000000,13000102,13999999,14000000,26000000,27000006,203000023)],[0,0,1,1,1,0,0,0,0])
        records=json.loads((HERE/'correlation.json').read_text())['evo_evidence']
        checked=0
        for e in records:
            if e['data_name']:
                self.assertEqual(e['evo_by_card_table'],e['evo_by_data_name'])
                self.assertEqual(e['evo_by_card_table'],e['cycle_hypothesis_evo'])
                checked+=1
        self.assertGreater(checked,10)
        for card in ('Knight','Tesla'):
            for form in (0,1):
                independent={(e['battle'],e['address'],e['generation']) for e in records
                             if e['card']==card and e['evo_by_card_table']==form
                             and e['evo_by_data_name']==form
                             and e['cycle_hypothesis_evo']==form
                             and any(s['coherent'] for s in e['samples'])}
                self.assertGreaterEqual(len(independent),5,(card,form))
    def test_source_generated_and_default_reader_functions_unchanged(self):
        old=SOURCE.read_text(); new=(HERE/'live_sampler2.c').read_text()
        self.assertEqual(new,generate())
        # Meaningful default-path guard: the original read_entities filtering,
        # player readers, discovery and emitters are unchanged byte-for-byte.
        for start,end in [('static int read_exact(','static int read_frame('),
                          ('static void emit_chain(','int main(')]:
            oldpart=old[old.index(start):old.index(end)]
            self.assertIn(oldpart,new)
        self.assertIn('int unified = argc >= 7;',new)
        self.assertIn('extended = argc == 8;',new)
        self.assertIn('if (extended && strcmp(argv[7], "--extended")) return 2;',new)
        self.assertIn('open(memory_path, O_RDONLY | O_CLOEXEC)',new)
        self.assertNotIn('pwrite(',new)

if __name__=='__main__': unittest.main(verbosity=2)
