let g:ycm_python_binary_path='C:\Program Files (x86)\Python36\python.exe'

function! Exe(program)
python << EOF
import vim
import subprocess
work_dir = vim.eval('g:work_path')
program = vim.eval('a:program')
if program == 'game':
	subprocess.Popen('python3 %smain.py' % work_dir, cwd=work_dir)
EOF
endfunction
command! -nargs=1 Exe :call Exe('<args>')

" 运行游戏
map <silent> <F5> :call Exe('game') <CR>
