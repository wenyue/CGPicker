let g:ycm_python_binary_path='C:\Program Files (x86)\Python36\python.exe'

function! Exe(program)
python << EOF
import vim
import subprocess
import os
work_dir = vim.eval('g:work_path')
program = vim.eval('a:program')
if program == 'game':
    handle = subprocess.Popen(
        'python3 %s' % os.path.join(work_dir, 'main.py'),
        cwd=work_dir,
        shell=True,
        stderr=subprocess.PIPE)
    print handle.stderr.read()
EOF
endfunction
command! -nargs=1 Exe :call Exe('<args>')

" 运行游戏
map <silent> <F5> :call Exe('game') <CR>
