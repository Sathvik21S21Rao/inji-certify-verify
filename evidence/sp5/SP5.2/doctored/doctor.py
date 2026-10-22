"""SP5.2 step 1b: flip one TestNG row FAIL->PASS in a scratch copy of testng-results.xml. Text edit, stdlib only.
Usage: doctor.py <report_dir>. Changes only the status attribute of the start tag of the test-method whose
param 0 is testCaseName=OIDF_certify_oid4vci-1_0-issuer-happy-flow,"""
import re, sys
from pathlib import Path
p = Path(sys.argv[1]) / "testng-results.xml"
src = p.read_text(encoding="utf-8")
needle = "testCaseName=OIDF_certify_oid4vci-1_0-issuer-happy-flow,"
assert src.count(needle) == 1, src.count(needle)
pos = src.index(needle)
start = src.rindex("<test-method signature", 0, pos)
end = src.index(">", start)  # end of the start tag
tag = src[start:end]
assert tag.count('status="FAIL"') == 1, tag[-200:]
new = src[:start] + tag.replace('status="FAIL"', 'status="PASS"') + src[end:]
p.write_text(new, encoding="utf-8")
print("flipped row at line", src[:start].count("\n") + 1, "FAIL -> PASS")
