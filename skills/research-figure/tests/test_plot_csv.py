from pathlib import Path
import sys, json, tempfile, unittest, hashlib, subprocess
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import plot_csv as plot
from figure_tools import figure_context

class FigureChecks(unittest.TestCase):
    def cfg(self,kind,**kwargs):
        return dict(kind=kind,input='input.csv',output_dir='out',x_label='x',y_label='y',synthetic=False,**kwargs)
    def rows(self,raw):
        return [(i+2,row) for i,row in enumerate(raw)]
    def test_missing_times_are_gaps_without_changing_values(self):
        c=self.cfg('timeseries',x='t',x_type='number',series=['y'],expected_interval=1)
        d,log=plot.prepare(c,{'t','y'},self.rows([{'t':'0','y':'2'},{'t':'1','y':''},{'t':'4','y':'8'}]))
        self.assertEqual(log['gap_before_csv_rows'],[4])
        f=plot.draw(c,d)
        ys=f.axes[0].lines[0].get_ydata()
        np.testing.assert_equal(ys,[2,np.nan,np.nan,8])
        plt.close(f)
    def test_parity_uses_common_rows_and_equal_axes(self):
        c=self.cfg('parity',actual='a',series=['p','q'])
        d,log=plot.prepare(c,{'a','p','q'},self.rows([{'a':'1','p':'2','q':'3'},{'a':'4','p':'','q':'6'},{'a':'5','p':'6','q':'7'}]))
        self.assertEqual(log['used_rows'],2)
        self.assertEqual(log['excluded_csv_rows'],[3])
        f=plot.draw(c,d); ax=f.axes[0]
        self.assertEqual(ax.get_xlim(),ax.get_ylim()); self.assertEqual(ax.get_aspect(),1)
        self.assertTrue(all(len(x.get_offsets())==2 for x in ax.collections)); plt.close(f)
    def test_unsorted_and_duplicate_times_fail(self):
        c=self.cfg('timeseries',x='t',x_type='number',series=['y'])
        for times in [('2','1'),('1','1')]:
            with self.assertRaisesRegex(ValueError,'strictly increasing'):
                plot.prepare(c,{'t','y'},self.rows([{'t':t,'y':'1'} for t in times]))
    def test_mixed_timezones_fail(self):
        c=self.cfg('timeseries',x='t',x_type='datetime',series=['y'])
        with self.assertRaisesRegex(ValueError,'Cannot mix'):
            plot.prepare(c,{'t','y'},self.rows([{'t':'2026-10-01','y':'1'},{'t':'2026-10-02T00:00:00+08:00','y':'2'}]))
    def test_duplicate_metrics_require_explicit_aggregation(self):
        c=self.cfg('metrics',category='c',model='m',value='v')
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            plot.prepare(c,{'c','m','v'},self.rows([{'c':'A','m':'B','v':'1'},{'c':'A','m':'B','v':'2'}]))
    def test_negative_error_rejected(self):
        c=self.cfg('metrics',category='c',model='m',value='v',error='e',error_type='SD')
        with self.assertRaisesRegex(ValueError,'nonnegative'):
            plot.prepare(c,{'c','m','v','e'},self.rows([{'c':'A','m':'B','v':'1','e':'-1'}]))
    def test_missing_metrics_not_zero_and_negative_baseline(self):
        c=self.cfg('metrics',category='c',model='m',value='v')
        d,log=plot.prepare(c,{'c','m','v'},self.rows([{'c':'A','m':'M1','v':'-2'},{'c':'B','m':'M2','v':'3'}]))
        self.assertEqual(len(log['missing_combinations']),2)
        f=plot.draw(c,d); self.assertEqual(sum(np.isnan(p.get_height()) for p in f.axes[0].patches),2)
        lo,hi=f.axes[0].get_ylim(); self.assertLess(lo,0); self.assertGreater(hi,0); plt.close(f)
    def test_context_restores_settings(self):
        original=plt.rcParams.copy()
        with figure_context(texts=['example'],profile='paper'):
            self.assertFalse(plt.rcParams['text.usetex'])
            self.assertAlmostEqual(plt.rcParams['figure.figsize'][0],90/25.4)
        self.assertEqual(plt.rcParams['font.family'],original['font.family'])
        self.assertEqual(plt.rcParams['figure.figsize'],original['figure.figsize'])
        self.assertEqual(plt.rcParams['text.usetex'],original['text.usetex'])
    def test_export_reproduce_nooverwrite_and_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            data=root/'input.csv'; data.write_text('x,y\n0,1\n1,3\n2,2\n')
            digest=hashlib.sha256(data.read_bytes()).hexdigest()
            c=self.cfg('timeseries',x='x',x_type='number',series=['y'],width_mm=150,height_mm=90)
            config=root/'config.json'; config.write_text(json.dumps(c))
            command=[sys.executable,str(ROOT/'scripts/plot_csv.py'),'--config',str(config)]
            run=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertEqual(hashlib.sha256(data.read_bytes()).hexdigest(),digest)
            log=json.loads((root/'out/render_log.json').read_text())
            self.assertEqual(log['warnings'],[])
            svg=ET.parse(root/'out/figure.svg').getroot()
            self.assertAlmostEqual(float(svg.attrib['width'][:-2]),150/25.4*72,places=4)
            self.assertAlmostEqual(float(svg.attrib['height'][:-2]),90/25.4*72,places=4)
            repeat=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(repeat.returncode,2)
            self.assertIn('already exist',repeat.stderr)
            replay=subprocess.run([sys.executable,str(root/'out/plot_csv.py'),'--config',str(root/'out/config.json'),'--overwrite'],capture_output=True,text=True)
            self.assertEqual(replay.returncode,0,replay.stderr)
    def test_unknown_fields_and_unexplained_errors_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unknown configuration'):
            plot.validate_config(self.cfg('parity',actual='a',series=['p'],smooth=True))
        with self.assertRaisesRegex(ValueError,'error_type'):
            plot.validate_config(self.cfg('metrics',category='c',model='m',value='v',error='e'))

if __name__=='__main__':
    unittest.main(verbosity=2)
