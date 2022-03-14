#!/usr/bin/env python3

import sys
import copy
import os
import time

# Universal Machine implementation

class UM:
    def __init__(self):
        self.regs=[0 for x in range(8)]
        self.arrays = []
        self.avail_arrays = []
        self.finger = 0
        self.debuglevel = 0
        self.numinst = 0
        self.timestamp = None

    def loadZeroArray(self, filename):
        sz = (os.path.getsize(filename)) // 4 + 1
        if len(self.arrays) == 0:
            self.arrays = [[0 for _ in range(sz)]]
        else:
            self.arrays[0] = [0 for _ in range(sz)]
        with open(filename,"rb") as fh:
            for i in range(sz):
                platter = fh.read(4)
                self.arrays[0][i] = int.from_bytes(platter,byteorder='big')

    def run(self):
        arrays = [None]
        arrays[0] = copy.copy(self.arrays[0])
        regs = [0 for _ in range(8)]
        avail_arrays = []
        finger=0
        keepRunning=True
        numinst =0
        while keepRunning:
            numinst += 1
            if numinst % 1000000 == 0:
                print("*", end="", flush=True)
            finger_at = arrays[0][finger]
            op = finger_at & 0xF0000000
            reg_a = (finger_at & 0b111000000) >> 6
            reg_b = (finger_at & 0b000111000) >> 3
            reg_c = finger_at & 0b000000111
    
            if op==0x00000000: # 0. Conditional Move.
                if regs[reg_c]!=0:
                    regs[reg_a]=regs[reg_b]
                finger += 1
            elif op==0x10000000: # 1. Array Index.
                regs[reg_a] = arrays[regs[reg_b]][regs[reg_c]]
                finger += 1
            elif op==0x20000000: # 2. Array Amendment.
                arrays[regs[reg_a]][regs[reg_b]] = regs[reg_c] 
                finger += 1
            elif op==0x30000000: # 3. Addition.
                regs[reg_a] = (regs[reg_b] + regs[reg_c]) & 0xFFFFFFFF
                finger += 1
            elif op==0x40000000: # 4. Multiplication.
                regs[reg_a] = (regs[reg_b] * regs[reg_c]) & 0xFFFFFFFF
                finger += 1
            elif op==0x50000000: # 5. Division.
                regs[reg_a] = (regs[reg_b] // regs[reg_c]) & 0xFFFFFFFF
                finger += 1
            elif op==0x50000000: # 6. Not-And.
                regs[reg_a] = (regs[reg_b] & regs[reg_c]) ^ 0xFFFFFFFF
                finger += 1
            elif op==0x70000000: # 7. Halt.
                keepRunning = False
            elif op==0x80000000: # 8. Allocation.
                use_platter = None
                if len(avail_arrays)>0:
                    use_platter = avail_arrays.pop()
                    arrays[use_platter] = [0 for _ in range(regs[reg_c])]  
                else:
                    arrays[use_platter].append([0 for _ in range(regs[reg_c])])
                finger += 1
            elif op==0x90000000: # 9. Abandonment.
                avail_arrays.append(regs[reg_c])
                finger += 1
            elif op==0xA0000000: # 10. Output.
                sys.stdout.write(chr(regs[reg_c]))
                sys.stdout.flush()
                finger += 1
            elif op==0xB0000000: # 11. Input.
                regs[reg_c] = ord(sys.stdin.read(1)) & 0x7f
                finger += 1
            elif op==0xC0000000: # 12. Load Program.
                if regs[reg_b] != 0:
                    arrays[0] = copy.copy(arrays[regs[reg_b]]) 
                finger = regs[reg_c]
            elif op==0xD0000000: # 13. Orthography
                reg_a = (finger_at & 0x0E000000) >> 25
                regs[reg_a] = finger_at & 0x01FFFFFF
                finger += 1
    
    def runDebug(self):
        self.timestamp = time.time()
        self.finger=0
        if self.debuglevel == 1:
            self.printInstr()
        while self.runCycle():
            self.numinst +=1
            if self.numinst % 1000000 == 0:
                print("*", end="", flush=True)
            if self.debuglevel == 1:
                self.printInstr()

    def printInstr(self):
        finger_at = self.arrays[0][self.finger]
        op = finger_at & 0xF0000000
        reg_a = (finger_at & 0b111000000) >> 6
        reg_b = (finger_at & 0b000111000) >> 3
        reg_c = finger_at & 0b000000111

        if op==0x00000000: # 0. Conditional Move.
            print(f'CMOV r{reg_a}=r{reg_b}:r{reg_c}!=0')
        elif op==0x10000000: # 1. Array Index.
            print(f'AIDX r{reg_a}=a{reg_b}[{reg_c}]')
        elif op==0x20000000: # 2. Array Amendment.
            print(f'AMND a[r{reg_a}][{reg_b}]=r{reg_c}')
        elif op==0x30000000: # 3. Addition.
            print(f'ADD r{reg_a}=r{reg_b}+r{reg_c}')
        elif op==0x40000000: # 4. Multiplication.
            print(f'MULT r{reg_a}=r{reg_b}*r{reg_c}')
        elif op==0x50000000: # 5. Division.
            print(f'DIV r{reg_a}=r{reg_b}*r{reg_c}')
        elif op==0x50000000: # 6. Not-And.
            print(f'NAND r{reg_a}=r{reg_b}*r{reg_c}')
        elif op==0x70000000: # 7. Halt.
            print(f'HALT')
        elif op==0x80000000: # 8. Allocation.
            print(f'ALLC a[r{reg_b}] with len r{reg_c}')
        elif op==0x90000000: # 9. Abandonment.
            print(f'ABND a[r{reg_c}]')
        elif op==0xA0000000: # 10. Output.
            print(f'OUT r{reg_c}')
        elif op==0xB0000000: # 11. Input.
            print(f'IN r{reg_c}')
        elif op==0xC0000000: # 12. Load Program.
            print(f'LOAD a[r{reg_b}]@r{reg_c}')
        elif op==0xD0000000: # 13. Orthography
            reg_a = (finger_at & 0x0E000000) >> 25
            print(f'ORTH r{reg_a}]={finger_at & 0x01FFFFFF}')

    def runCycle(self):
        finger_at = self.arrays[0][self.finger]
        op = finger_at & 0xF0000000
        reg_a = (finger_at & 0b111000000) >> 6
        reg_b = (finger_at & 0b000111000) >> 3
        reg_c = finger_at & 0b000000111

        if op==0x00000000: # 0. Conditional Move.
            # The register A receives the value in register B,
            # unless the register C contains 0.
            if self.regs[reg_c]!=0:
                self.regs[reg_a]=self.regs[reg_b]
            self.finger += 1
        elif op==0x10000000: # 1. Array Index.
            # The register A receives the value stored at offset
            # in register C in the array identified by B.
            self.regs[reg_a] = self.arrays[self.regs[reg_b]][self.regs[reg_c]]
            self.finger += 1
        elif op==0x20000000: # 2. Array Amendment.
            # The array identified by A is amended at the offset
            # in register B to store the value in register C.
            self.arrays[self.regs[reg_a]][self.regs[reg_b]] = self.regs[reg_c] 
            self.finger += 1
        elif op==0x30000000: # 3. Addition.
            # The register A receives the value in register B plus 
            # the value in register C, modulo 2^32.
            self.regs[reg_a] = (self.regs[reg_b] + self.regs[reg_c]) & 0xFFFFFFFF
            self.finger += 1
        elif op==0x40000000: # 4. Multiplication.
            # The register A receives the value in register B times
            # the value in register C, modulo 2^32.
            self.regs[reg_a] = (self.regs[reg_b] * self.regs[reg_c]) & 0xFFFFFFFF
            self.finger += 1
        elif op==0x50000000: # 5. Division.
            # The register A receives the value in register B
            # divided by the value in register C, if any, where
            # each quantity is treated treated as an unsigned 32
            # bit number.
            self.regs[reg_a] = (self.regs[reg_b] // self.regs[reg_c]) & 0xFFFFFFFF
            self.finger += 1
        elif op==0x50000000: # 6. Not-And.
            # Each bit in the register A receives the 1 bit if
            # either register B or register C has a 0 bit in that
            # position.  Otherwise the bit in register A receives
            # the 0 bit.
            self.regs[reg_a] = (self.regs[reg_b] & self.regs[reg_c]) ^ 0xFFFFFFFF
            self.finger += 1
        elif op==0x70000000: # 7. Halt.
            # The universal machine stops computation.
            return False
        elif op==0x80000000: # 8. Allocation.
            # A new array is created with a capacity of platters
            # commensurate to the value in the register C. This
            # new array is initialized entirely with platters
            # holding the value 0. A bit pattern not consisting of
            # exclusively the 0 bit, and that identifies no other
            # active allocated array, is placed in the B register.
            use_platter = None
            if len(self.avail_arrays)>0:
                use_platter = self.avail_arrays.pop()
                self.arrays[use_platter] = [0 for _ in range(self.regs[reg_c])]  
            else:
                self.arrays[use_platter].append([0 for _ in range(self.regs[reg_c])])
            self.finger += 1
        elif op==0x90000000: # 9. Abandonment.
            #The array identified by the register C is abandoned.
            #Future allocations may then reuse that identifier.
            self.avail_arrays.append(self.regs[reg_c])
            self.finger += 1
        elif op==0xA0000000: # 10. Output.
            # The value in the register C is displayed on the console
            # immediately. Only values between and including 0 and 255
            # are allowed.
            sys.stdout.write(chr(self.regs[reg_c]))
            sys.stdout.flush()
            self.finger += 1
        elif op==0xB0000000: # 11. Input.
            # The universal machine waits for input on the console.
            # When input arrives, the register C is loaded with the
            # input, which must be between and including 0 and 255.
            # If the end of input has been signaled, then the 
            # register C is endowed with a uniform value pattern
            # where every place is pregnant with the 1 bit.
            self.regs[reg_c] = ord(sys.stdin.read(1)) & 0x7f
            self.finger += 1
        elif op==0xC0000000: # 12. Load Program.
            # The array identified by the B register is duplicated
            # and the duplicate shall replace the '0' array,
            # regardless of size. The execution finger is placed
            # to indicate the platter of this array that is
            # described by the offset given in C, where the value
            # 0 denotes the first platter, 1 the second, et
            # cetera.
            # The '0' array shall be the most sublime choice for
            # loading, and shall be handled with the utmost
            # velocity.
            if self.regs[reg_b] != 0:
               self.arrays[0] = copy.copy(self.arrays[self.regs[reg_b]]) 
            self.finger = self.regs[reg_c]
        elif op==0xD0000000: # 13. Orthography
            reg_a = (finger_at & 0x0E000000) >> 25
            self.regs[reg_a] = finger_at & 0x01FFFFFF
            self.finger += 1
        return True
