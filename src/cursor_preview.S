.intel_syntax noprefix
.code32
.section .text
.global render_wrapper
.set original_render_update, 0x406270
.set original_sprite_update, 0x421800

# Preview immediately BEFORE drawing; tail-call the original renderer update.
# Preserve the renderer's arguments, registers, flags, and return behavior.
render_wrapper:
    pushfd
    pushad
    call preview_cursor
    popad
    popfd
    jmp original_render_update

# Only the visible cursor coordinates are previewed. Authoritative coordinates,
# button states, wheel state, and the buffered event queue remain unchanged.
preview_cursor:
    push ebp
    mov ebp, esp
    sub esp, 0xa20
    push ebx
    push esi
    push edi
    call image_anchor
image_anchor:
    pop ebx
    sub ebx, OFFSET image_anchor - 0x400000
    cmp DWORD PTR [ebx+0x343c08], 0
    je done
    mov eax, DWORD PTR [ebx+0x3498fc]
    test eax,eax
    je done
    mov esi, DWORD PTR [eax+0x10]
    test esi,esi
    je done
    mov ecx, DWORD PTR [esi+0x848]
    test ecx,0x10
    jne done
    and ecx,3
    cmp ecx,3
    jne done
    mov edi, DWORD PTR [eax+0x14]
    test edi,edi
    je done
    mov edi, DWORD PTR [edi]
    test edi,edi
    je done
    cmp DWORD PTR [edi],2
    jne done
    mov eax, DWORD PTR [eax+0x78]
    test eax,eax
    je done
    mov eax, DWORD PTR [eax+0x7c]
    test eax,eax
    je done
    cmp DWORD PTR [eax+0x594],0
    je done
    mov ecx, DWORD PTR [eax+0x588]
    mov DWORD PTR [ebp-0x10],ecx
    mov ecx, DWORD PTR [eax+0x58c]
    mov DWORD PTR [ebp-0x14],ecx
    mov eax, DWORD PTR [ebx+0x343e68]
    test eax,eax
    je done
    mov DWORD PTR [ebp-4],128
    mov DWORD PTR [ebp-8],0
    mov DWORD PTR [ebp-12],0
    push 1                         # DIGDD_PEEK: do not consume events
    lea edx,[ebp-4]
    push edx
    lea edx,[ebp-0xa20]
    push edx
    push 20
    mov ecx,DWORD PTR [eax]
    push eax
    call DWORD PTR [ecx+0x28]
    test eax,eax
    js done
    mov ecx,DWORD PTR [ebp-4]
    cmp ecx,128
    ja done
    lea edx,[ebp-0xa20]
    test ecx,ecx
    je position
events:
    cmp DWORD PTR [edx],0
    jne check_y
    fild DWORD PTR [edx+4]
    fadd DWORD PTR [ebp-8]
    fstp DWORD PTR [ebp-8]
    jmp next_event
check_y:
    cmp DWORD PTR [edx],4
    jne next_event
    fild DWORD PTR [edx+4]
    fadd DWORD PTR [ebp-12]
    fstp DWORD PTR [ebp-12]
next_event:
    add edx,20
    dec ecx
    jnz events
position:
    fld DWORD PTR [ebp-8]
    fmul DWORD PTR [esi+0x14]
    fadd DWORD PTR [esi+0x84c]
    fstp DWORD PTR [ebp-8]
    fld DWORD PTR [ebp-12]
    fmul DWORD PTR [esi+0x14]
    fadd DWORD PTR [esi+0x850]
    fstp DWORD PTR [ebp-12]
    # Clamp visible coordinates to the same full-screen bounds as the game.
    lea edx,[ebp-8]
    lea ecx,[ebp-0x10]
    call clamp_axis
    lea edx,[ebp-12]
    lea ecx,[ebp-0x14]
    call clamp_axis
    mov eax,DWORD PTR [ebp-8]
    mov DWORD PTR [esi+0x824],eax
    mov eax,DWORD PTR [ebp-12]
    mov DWORD PTR [esi+0x828],eax
    lea eax,[esi+0x824]
    push eax
    mov ecx,edi
    call original_sprite_update
done:
    pop edi
    pop esi
    pop ebx
    mov esp,ebp
    pop ebp
    ret

# EDX points to a float coordinate; ECX points to the integer upper bound.
clamp_axis:
    fldz
    fcomp DWORD PTR [edx]
    fnstsw ax
    test ah,0x41
    jnz nonnegative
    mov DWORD PTR [edx],0
nonnegative:
    fild DWORD PTR [ecx]
    fcom DWORD PTR [edx]
    fnstsw ax
    test ah,1
    jz in_bounds
    fstp DWORD PTR [edx]
    ret
in_bounds:
    fstp st(0)
    ret
