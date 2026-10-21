.intel_syntax noprefix
.code32
.section .text
.global resolution_filter
# Reconstructed from the corrected, released machine code.
# EAX points to the mode's width/height. Keep the original enumeration loop.
# The original loop separately checks the pixel format and advances modes.
resolution_filter:
    cmp DWORD PTR [eax], 1024
    jne mode_1280_1024
    cmp DWORD PTR [eax+4], 768
    je accepted
mode_1280_1024:
    cmp DWORD PTR [eax], 1280
    jne mode_1600_1200
    cmp DWORD PTR [eax+4], 1024
    je accepted
mode_1600_1200:
    cmp DWORD PTR [eax], 1600
    jne mode_1280_720
    cmp DWORD PTR [eax+4], 1200
    je accepted
mode_1280_720:
    cmp DWORD PTR [eax], 1280
    jne mode_1920_1080
    cmp DWORD PTR [eax+4], 720
    je accepted
mode_1920_1080:
    cmp DWORD PTR [eax], 1920
    jne mode_2560_1440
    cmp DWORD PTR [eax+4], 1080
    je accepted
mode_2560_1440:
    cmp DWORD PTR [eax], 2560
    jne mode_3840_2160
    cmp DWORD PTR [eax+4], 1440
    je accepted
mode_3840_2160:
    cmp DWORD PTR [eax], 3840
    jne rejected
    cmp DWORD PTR [eax+4], 2160
    je accepted
rejected:
    jmp 0x504984
    .fill 4, 1, 0x90
# The separate depth check branches here to rejoin the mode-advance path.
skip_depth:
    jmp 0x504976
    nop
accepted:
