" let g:ycm_python_binary_path='C:\Program Files (x86)\Python36\python.exe'

let g:enable_ycm = 1

function! Exe(program)
python << EOF
import vim
import subprocess
import os
work_dir = vim.eval('g:work_path')
program = vim.eval('a:program')
if program == 'game':
    subprocess.Popen(
    'python3 %s' % os.path.join(work_dir, 'main.py'),
    cwd=work_dir,
    shell=True,
    stderr=subprocess.PIPE)
EOF
endfunction
command! -nargs=1 Exe :call Exe('<args>')

" 运行游戏
map <silent> <F5> :call Exe('game') <CR>
