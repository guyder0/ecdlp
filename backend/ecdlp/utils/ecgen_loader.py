import json
from fastecdsa.curve import Curve
from fastecdsa.point import Point
from ..exceptions import InvalidCurveError

class ECGenLoader:
    @staticmethod
    def parse_hex(val):
        if isinstance(val, str) and val.startswith('0x'):
            return int(val, 16)
        return int(val)

    @classmethod
    def load_from_json_file(cls, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        tasks = []
        for entry in data:
            try:
                p = cls.parse_hex(entry['field']['p'])
                a = cls.parse_hex(entry['a'])
                b = cls.parse_hex(entry['b'])
                
                for sg in entry.get('subgroups', []):
                    gx = cls.parse_hex(sg['x'])
                    gy = cls.parse_hex(sg['y'])
                    g_order = cls.parse_hex(sg['order'])
                    
                    curve = Curve(
                        name="TestCurve",
                        p=p,
                        a=a,
                        b=b,
                        q=g_order,
                        gx=gx,
                        gy=gy
                    )
                    
                    g_pt = Point(gx, gy, curve=curve)
                    
                    tasks.append({
                        'curve': curve,
                        'generator': g_pt,
                        'order': g_order,
                    })
            except KeyError as e:
                raise InvalidCurveError(f"Missing field in JSON: {e}")
                
        return tasks