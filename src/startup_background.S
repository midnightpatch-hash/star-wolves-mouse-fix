.intel_syntax noprefix
.code32
.section .text
.global startup_background
# Reconstructed from the released v1.1.0 hook. The original window-registration
# code stores the cursor handle here before calling GetStockObject; retain
# that stack store while replacing the brush argument with BLACK_BRUSH (4).
startup_background:
    mov DWORD PTR [esp+0x24], eax
    push 4
    jmp 0x490ff8
