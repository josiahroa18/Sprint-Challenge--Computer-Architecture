import sys

class CPU:

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True

        # Set the stack pointer to R7
        self.reg[7] = 0xF4

        # Set the flag register
        self.flag = 0b00000000

        self.branch_table = {
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b00000001: self.HLT,
            0b10100010: self.MUL,
            0b10100000: self.ADD,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE
        }

    # Should accept the address to read and return the value
    def ram_read(self, address):
        return self.ram[address]

    # Should accept an address and value and store the value at that address
    def ram_write(self, address, value):
        self.ram[address] = value

    def LDI(self):
        index = self.ram[self.pc + 1]
        value = self.ram[self.pc + 2]
        self.reg[index] = value
        self.pc += 3

    def PRN(self):
        value = self.reg[self.ram[self.pc + 1]]
        print(value)
        self.pc += 2

    def HLT(self):
        self.running = False

    def MUL(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('MUL', reg_a, reg_b)

    def ADD(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('ADD', reg_a, reg_b)

    def PUSH(self):
        self.reg[7] -= 1
        register_index = self.ram[self.pc + 1]
        self.ram[self.reg[7]] = self.reg[register_index]
        self.pc += 2

    def POP(self):
        register_index = self.ram[self.pc + 1]
        self.reg[register_index] = self.ram[self.reg[7]]
        self.reg[7] += 1
        self.pc += 2

    def CALL(self):
        # Store next instruction in the stack
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.pc + 2
        # Move program counter to address stored in register
        register_index = self.ram[self.pc + 1]
        self.pc = self.reg[register_index]

    def RET(self):
        # Pop from the stack
        address = self.ram[self.reg[7]]
        register_index = self.ram[self.pc + 1]
        self.reg[register_index] = self.ram[self.reg[7]]
        self.reg[7] += 1
        # Update program counter
        self.pc = address

    def CMP(self):
        reg_a = self.ram[self.pc + 1]
        reg_b = self.ram[self.pc + 2]
        self.alu('CMP', reg_a, reg_b)

    def JMP(self):
        register_index = self.ram[self.pc + 1]
        address = self.reg[register_index]
        self.pc = address

    def JEQ(self):
        register_index = self.ram[self.pc + 1]
        if self.flag == 1:
            self.pc = self.reg[register_index] # Set program counter to value at given register
        else:
            self.pc += 2

    def JNE(self):
        register_index = self.ram[self.pc + 1]
        if self.flag == 0:
            self.pc = self.reg[register_index] # Set program counter to value at given register
        else:
            self.pc += 2

    def load(self, fileName):
        address = 0
        with open(fileName) as file:
            for line in file:
                line = line.split('#')
                try:
                    instruction = int(line[0], 2)
                    self.ram[address] = instruction
                    address += 1
                except ValueError:
                    continue
                    
    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
            self.pc += 3
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 1 #0b00000001
            self.pc += 3
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while self.running:
            ir = self.ram[self.pc]
            try:
                self.branch_table[ir]()
            except:
                raise Exception(f"Unknown instruction: {self.ram[self.pc]}")