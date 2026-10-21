.intel_syntax noprefix
.section .text
.global increase, decrease, scale_display, normalize_display, store_ecx, store_edi, render_router, patch_end
.equ ROOT, 0x7498fc
.equ GET_CHILD, 0x464d70
.equ FTOI, 0x6401f4
.equ MOUSE_NAME, 0x6a9a0c
.equ GET_SIZE, 0x46b610
.equ SET_SIZE, 0x46b7a0
.equ DRAW, 0x46b780

increase:
    push ecx
    mov ecx, 1
    jmp change
decrease:
    push ecx
    mov ecx, -1
change:
    push ebx
    push esi
    push edi
    push ebp
    mov ebp, ecx
    mov esi, [esp+24]
    call 1f
1:  pop ebx
    sub ebx, offset 1b
    fld dword ptr [esi+0x64]
    fmul dword ptr [ebx+eight]
    fadd dword ptr [ebx+half]
    call FTOI
    call clamp_index
    add eax, ebp
    call clamp_index
    mov edi, eax
    push eax
    fild dword ptr [esp]
    fmul dword ptr [ebx+eighth]
    fstp dword ptr [esi+0x64]
    add esp, 4
    mov eax, [ebx+ROOT]
    test eax, eax
    jz 2f
    mov edx, [eax+0x10]
    test edx, edx
    jz 2f
    mov eax, [esi+0x64]
    mov [edx+0x14], eax
2:  push 1
    lea eax, [ebx+MOUSE_NAME]
    push eax
    mov ecx, [esi+0x1c]
    call GET_CHILD
    mov ecx, edi
    call configure_bar
    pop ebp
    pop edi
    pop esi
    pop ebx
    pop ecx
    ret

clamp_index:
    cmp eax, 1
    jge 1f
    mov eax, 1
1:  cmp eax, 20
    jle 2f
    mov eax, 20
2:  ret

scale_display:
    push ebx
    call 1f
1:  pop ebx
    sub ebx, offset 1b
    fmul dword ptr [ebx+eight]
    fadd dword ptr [ebx+half]
    call FTOI
    call clamp_index
    pop ebx
    ret

normalize_display:
    push ebx
    push edi
    call scale_display
    mov edi, eax
    call 1f
1:  pop ebx
    sub ebx, offset 1b
    push eax
    fild dword ptr [esp]
    fmul dword ptr [ebx+eighth]
    fstp dword ptr [esi+0x64]
    add esp, 4
    mov eax, [ebx+ROOT]
    test eax, eax
    jz 2f
    mov edx, [eax+0x10]
    test edx, edx
    jz 2f
    mov ecx, [esi+0x64]
    mov [edx+0x14], ecx
2:  mov eax, edi
    pop edi
    pop ebx
    ret

store_edi:
    push ecx
    mov ecx, edi
    call configure_bar
    pop ecx
    ret
store_ecx:
    call configure_bar
    ret
configure_bar:
    test eax, eax
    jz 1f
    mov [eax+0x178], ecx
    mov dword ptr [eax+0x17c], 0
    mov dword ptr [eax+0x180], 20
1:  ret

# Other step bars keep the original renderer.
render_router:
    cmp dword ptr [ecx+0x180], 20
    jne original_render
    cmp dword ptr [ecx+0x17c], 0
    jne original_render
    cmp dword ptr [ecx+0x130], 22
    jl original_render
    jmp render_twenty
original_render:
    sub esp, 0x10
    push ebx
    push ebp
    jmp 0x4840f5

render_twenty:
    push ebx
    push ebp
    push esi
    push edi
    sub esp, 40
    mov esi, ecx
    xor eax, eax
    mov [esp], eax
    mov [esp+4], eax
    lea eax, [esp]
    push eax
    mov eax, [esi]
    call [eax+0x54]
    mov eax, [esi+0x178]
    test eax, eax
    jge 1f
    xor eax, eax
1:  cmp eax, 20
    jle 2f
    mov eax, 20
2:  mov [esi+0x178], eax
    mov [esp+36], eax
    mov eax, [esi+0x130]
    sub eax, 2
    mov [esp+28], eax
    mov ecx, [esi+0x188]
    call GET_SIZE
    mov edx, [eax]
    mov eax, [eax+4]
    mov [esp+16], edx
    mov [esp+20], eax
    lea eax, [esp]
    push eax
    mov ecx, [esi+0x184]
    call DRAW
    mov eax, [esp]
    add eax, 2
    mov [esp+24], eax
    xor ebp, ebp
    mov ebx, 1
next_segment:
    cmp ebx, [esp+36]
    jg segments_done
    mov eax, ebx
    imul eax, [esp+28]
    cdq
    mov ecx, 20
    idiv ecx
    mov edi, eax
    sub eax, ebp
    mov [esp+8], eax
    mov eax, [esp+20]
    mov [esp+12], eax
    lea eax, [esp+8]
    push eax
    mov ecx, [esi+0x188]
    call SET_SIZE
    mov eax, [esp+24]
    add eax, ebp
    mov [esp], eax
    lea eax, [esp]
    push eax
    mov ecx, [esi+0x188]
    call DRAW
    mov ebp, edi
    inc ebx
    jmp next_segment
segments_done:
    # Restore source dimensions after every render.
    lea eax, [esp+16]
    push eax
    mov ecx, [esi+0x188]
    call SET_SIZE
    mov eax, [esp+28]
    sub eax, ebp
    mov [esp+8], eax
    mov eax, [esi+0x134]
    mov [esp+12], eax
    lea eax, [esp+8]
    push eax
    mov ecx, [esi+0x18c]
    call SET_SIZE
    mov eax, [esp+24]
    add eax, ebp
    mov [esp], eax
    lea eax, [esp]
    push eax
    mov ecx, [esi+0x18c]
    call DRAW
    add esp, 40
    pop edi
    pop esi
    pop ebp
    pop ebx
    ret

.balign 4
eight: .float 8.0
half: .float 0.5
eighth: .float 0.125
patch_end:
