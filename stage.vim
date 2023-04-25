let SessionLoad = 1
let s:so_save = &g:so | let s:siso_save = &g:siso | setg so=0 siso=0 | setl so=-1 siso=-1
let v:this_session=expand("<sfile>:p")
silent only
silent tabonly
cd ~/Rotating_stage
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
let s:shortmess_save = &shortmess
if &shortmess =~ 'A'
  set shortmess=aoOA
else
  set shortmess=aoO
endif
badd +1 fsm_test.py
badd +248 rotate_stage_fsm.py
badd +1 scenarios.py
badd +1 ~/alx-higher_level_programming/0x07-python-test_driven_development/102-tests.py
badd +1 ~/alx-higher_level_programming/0x07-python-test_driven_development/0-add_integer.py
badd +1 ~/alx-higher_level_programming/0x07-python-test_driven_development/0-main.py
badd +1 ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py
badd +9 test_fsm_operation.py
badd +1 copy.py
argglobal
%argdel
$argadd fsm_test.py
$argadd rotate_stage_fsm.py
$argadd scenarios.py
set stal=2
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabnew +setlocal\ bufhidden=wipe
tabrewind
edit fsm_test.py
argglobal
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 1 - ((0 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 1
normal! 0
tabnext
edit rotate_stage_fsm.py
argglobal
2argu
balt fsm_test.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 271 - ((49 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 271
normal! 0
tabnext
edit scenarios.py
argglobal
3argu
balt fsm_test.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 49 - ((48 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 49
normal! 039|
tabnext
edit ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py
argglobal
1argu
if bufexists(fnamemodify("~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py", ":p")) | buffer ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py | else | edit ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py | endif
if &buftype ==# 'terminal'
  silent file ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py
endif
balt fsm_test.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 44 - ((43 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 44
normal! 05|
lcd ~/Rotating_stage
tabnext
edit ~/Rotating_stage/test_fsm_operation.py
argglobal
if bufexists(fnamemodify("~/Rotating_stage/test_fsm_operation.py", ":p")) | buffer ~/Rotating_stage/test_fsm_operation.py | else | edit ~/Rotating_stage/test_fsm_operation.py | endif
if &buftype ==# 'terminal'
  silent file ~/Rotating_stage/test_fsm_operation.py
endif
balt ~/alx-higher_level_programming/0x0C-python-almost_a_circle/tests/test_models/test_rectangle.py
setlocal fdm=manual
setlocal fde=0
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
silent! normal! zE
let &fdl = &fdl
let s:l = 10 - ((5 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
keepjumps exe s:l
normal! zt
keepjumps 10
normal! 05|
lcd ~/Rotating_stage
tabnext 5
set stal=1
if exists('s:wipebuf') && len(win_findbuf(s:wipebuf)) == 0 && getbufvar(s:wipebuf, '&buftype') isnot# 'terminal'
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20
let &shortmess = s:shortmess_save
let s:sx = expand("<sfile>:p:r")."x.vim"
if filereadable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &g:so = s:so_save | let &g:siso = s:siso_save
nohlsearch
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
