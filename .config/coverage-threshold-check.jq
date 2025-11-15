# Coverage threshold check script
# Thresholds: Line > 80%, Branch > 70%, Function > 85%
# Note: Skip threshold check if count is 0 (no branches/lines/functions to cover)

.data[0].totals as $s |
($s.lines.percent // 0) as $line |
($s.lines.count // 0) as $line_count |
($s.branches.percent // 0) as $branch |
($s.branches.count // 0) as $branch_count |
($s.functions.percent // 0) as $func |
($s.functions.count // 0) as $func_count |

def check(actual; count; threshold; name):
  if count == 0 then
    "⚠️  \(name) coverage: N/A (no \(name | ascii_downcase) to cover)"
  elif actual >= threshold then
    "✅ \(name) coverage: \(actual)% (threshold: \(threshold)%)"
  else
    "❌ \(name) coverage \(actual)% is below threshold of \(threshold)%"
  end;

check($line; $line_count; 80; "Line"),
check($branch; $branch_count; 70; "Branch"),
check($func; $func_count; 85; "Function"),

# Only check thresholds for metrics that have items to cover
(if $line_count > 0 and $line < 80 then false else true end) and
(if $branch_count > 0 and $branch < 70 then false else true end) and
(if $func_count > 0 and $func < 85 then false else true end) |
if . then
  "Coverage thresholds met. ✅"
else
  "Coverage thresholds not met. Failing CI.",
  false
end
