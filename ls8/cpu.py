"""CPU functionality."""

import sys

#OPCODES
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
POP = 0b01000110
PUSH = 0b01000101
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

LT = 0b00000100
GT = 0b00000010
EQ = 0b00000001

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Program Counter, address of the currently executing instruction
        self.pc = 0
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.fl = 0
        # BT cleans up code so u can reuse and not have to type it out errytime
        self.button = {
            LDI: self.ldi,
            PRN: self.prn,
            HLT: self.hlt,
            ADD: self.add,
            MUL: self.mul,
            POP: self.pop,
            PUSH: self.push,
            CALL: self.call,
            RET: self.ret,
            CMP: self.operation_cmp,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne
        }
    
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])

    def hlt(self, operand_a, operand_b):
        sys.exit(0)

    def add(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)

    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)

    def pop(self, operand_a, operand_b):
        self.reg[operand_a] = self.pop_val()

    def push(self, operand_a, operand_b):
        self.push_val(self.reg[operand_a])

    def call(self, operand_a, operand_b):
        self.push_val(self.pc + 2)
        self.pc = self.reg[operand_a]

    def ret(self, operand_a, operand_b):
        self.pc = self.pop_val()

    def operation_cmp(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)

    def jmp(self, operand_a, operand_b):
        self.pc = self.reg[operand_a]

    def jeq(self, operand_a, operand_b):
        if self.fl == EQ:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2

    def jne(self, operand_a, operand_b):
        if not self.fl == EQ:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2



    def load(self, filename):
        """Load a program into memory."""
        try:
            address = 0
            #open the file
            with open(sys.argv[1]) as f:
                #read every line
                for line in f:
                    #parse out comments
                    comment_split = line.strip().split("#")
                    # Cast number string to int
                    value = comment_split[0].strip()
                    #ignore blank lines
                    if value == "":
                        continue
                    instruction = int(value, 2)
                    #populate memory array
                    self.ram[address] = instruction
                    address += 1

        except:
            print("cant find file")
            sys.exit(2)


    def ram_read(self, memory):
        #accept addres to (mem) and return
        #adress to write
        #mem = memory adress register/ memory_data = memory data register
        memory_data = self.ram[memory]
        return memory_data

    def ram_write(self, memory_data, memory):
        # Accept a value to write (memory_data), and address
        # to write it to (mem)
        self.ram[memory] = memory_data

    def push_val(self, val):
        self.reg[SP] -= 1
        self.ram_write(val, self.reg[SP])

    def pop_val(self):
        val = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return val


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op ==  "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = LT
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = GT
            else:
                self.fl = EQ
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        
        """Run the CPU."""

        while True:
            #pulling instructions through memory
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            instruction_length = (instruction >> 6) + 1
            
            instruction_set_pc = ((instruction >> 4) & 0b1) == 1
            if instruction in self.button:
                self.button[instruction](operand_a, operand_b)
            #check if opcode instructions sets the pc
            # If not, increment pc by instruction length
            if instruction_set_pc != 1:
                self.pc += instruction_length