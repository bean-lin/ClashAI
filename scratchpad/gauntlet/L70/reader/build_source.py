"""Generate the standalone C source by minimal, assertion-checked insertions.
This only writes source; it never invokes a compiler, WSL, adb, or git.
"""
import hashlib
from pathlib import Path

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parents[3]/'research/ext/cr_live/upstream/native_core/mumu_live_private_sampler.c'

def generate():
    original=SOURCE.read_text()
    src=original
    def replace(old,new):
        nonlocal src
        assert src.count(old)==1, old
        src=src.replace(old,new)
    helper=(HERE/'extension_impl.inc').read_text()
    replace('static int read_frame(',helper+'\nstatic int read_frame(')
    replace('  read_exact(fd, battle + 0x1BC,',
            '  if (extended && unified) read_extended_objects(fd, libg, frame);\n  read_exact(fd, battle + 0x1BC,')
    replace('if (argc != 5 && argc != 7)', 'if (argc != 5 && argc != 7 && argc != 8)')
    replace('ROOT_CONTEXT_OFFSET [--unified MAX_FRAMES(0=unlimited)]',
            'ROOT_CONTEXT_OFFSET [--unified MAX_FRAMES(0=unlimited) [--extended]]')
    replace('  int unified = argc == 7;',
            '  int unified = argc >= 7;\n  extended = argc == 8;\n  if (extended && strcmp(argv[7], "--extended")) return 2;')
    replace('      active = read_frame(',
            '      if (extended) memset(&extra, 0, sizeof extra);\n      active = read_frame(')
    replace("        if (i) putchar(',');\n        printf(\"{\\\"address\\\":", 
            "        if (i) putchar(',');\n        if (extended) { emit_extended_entity(e); continue; }\n        printf(\"{\\\"address\\\":")
    replace('    printf(",\\\"sample_monotonic_us\\\":',
            '    if (extended) emit_extra(active, coherent);\n    printf(",\\\"sample_monotonic_us\\\":')
    header='''/*
 * Live sampler v2, live x86_64 build 160402012. READ-ONLY /proc/PID/mem.
 * Build in WSL, from this directory (NOT compiled in the sandbox):
 *   gcc -O2 -static -o live_sampler2 live_sampler2.c
 * Run: live_sampler2 PID 100 0x1aeef98 0x18 --unified 0 [--extended]
 * Only --extended adds evo and the projectiles/effects arrays, and admits the
 * table-13 evolution bodies that v1 incorrectly filters. Native IDs preserved.
 * Default formatting and original reader functions are retained. The new
 * vtables are pinned to this build; do not reuse on another game update.
 *
 * LEAD CHECKLIST after compiling:
 * [ ] Confirm x86_64 static ELF, O_RDONLY and no native-game calls/input.
 * [ ] Verify installed package build and libg identity before enabling fields.
 * [ ] Run standalone v1 and v2 default ~60s without disturbing the live bot.
 *     Use /data/local/tmp/re_* paths only under this task's write boundary.
 * [ ] Diff raw default JSON; record result. Independent reader_pid, sequence,
 *     sample_monotonic_us/read_us and sampling times naturally differ. Do not
 *     claim byte-identical live streams. For the formatter contract, compare
 *     deterministic identical frame fixtures byte-for-byte; also compare
 *     coherent same-tick live payloads with only documented volatile exclusions.
 * [ ] Compare --extended against Python reference on identical captured bytes.
 *     Check empty/inactive/error cases, projectile target and moving position,
 *     effect countdown (NOT sandbox elapsed time); negative timers emit null.
 * [ ] Confirm five independently labelled base/evolved Knight AND Tesla bodies
 *     per class, cast cycle and names; check opponents on an existing video if
 *     available. No new screenshot/video capture under the task authorization.
 * [ ] Measure read_us/coherence and adb load; do not replace the running reader
 *     or integrate with the live pilot under this task.
 *
 * Source SHA256: '''+hashlib.sha256(SOURCE.read_bytes()).hexdigest()+'''
 * Evidence/limitations: FINDINGS.md, correlation.json, capture_*.jsonl.
 */
'''
    return header+src

if __name__=='__main__':
    out=HERE/'live_sampler2.c'
    # Existing generated files belong to this task; never overwrite upstream.
    out.write_text(generate(),encoding='utf-8',newline='\n')
    print('generated',out)
