__author__ = 'akke'

import sys
from enum import Enum
import re


class Lexem(Enum):
    CLASS_NULL = 0

    CLASS_BEGIN_WORD = 1
    CLASS_END_WORD = 2
    CLASS_VAR_WORD = 3
    CLASS_BOOLEAN_WORD = 4

    CLASS_AND = 5
    CLASS_NOT = 6
    CLASS_OR = 7
    CLASS_XOR = 8

    CLASS_COMMA = 9
    CLASS_SEMICOLON = 10
    CLASS_EQUAL = 11
    CLASS_LBRACKET = 12
    CLASS_RBRACKET = 13
    CLASS_COLON = 14
    CLASS_ZERO = 15
    CLASS_ONE = 16

    CLASS_IDENTIFIER = 20
    CLASS_UNKNOWN = 21

    def get_view(self):
        values = ['<End>', 'Begin', 'End', 'Var', 'Boolean', '.AND.', '.NOT.', '.OR.', '.XOR.', ',', ';', '=', '(', ')', ':', '0', '1']
        if self.value < len(values):
            return values[self.value]
        return None


class Parser(object):
    value = None
    code_line = 1
    position = 0
    content = None

    def next_token(self):
        self.value = None
        while True:
            try:
                c = self.content[self.position]
            except:
                return Lexem.CLASS_NULL

            if c == ',':
                self.position += 1
                return Lexem.CLASS_COMMA
            if c == ';':
                self.position += 1
                return Lexem.CLASS_SEMICOLON
            if c == '=':
                self.position += 1
                return Lexem.CLASS_EQUAL
            if c == '(':
                self.position += 1
                return Lexem.CLASS_LBRACKET
            if c == ')':
                self.position += 1
                return Lexem.CLASS_RBRACKET
            if c == ':':
                self.position += 1
                return Lexem.CLASS_COLON
            if c == '0':
                self.position += 1
                return Lexem.CLASS_ZERO
            if c == '1':
                self.position += 1
                return Lexem.CLASS_ONE

            if c == '.':  # boolean operators
                if self.content[self.position:self.position + 4] == '.OR.':
                    self.position += 4
                    return Lexem.CLASS_OR
                operator = self.content[self.position:self.position + 5]
                if operator == '.NOT.':
                    self.position += 5
                    return Lexem.CLASS_NOT
                if operator == '.XOR.':
                    self.position += 5
                    return Lexem.CLASS_XOR
                if operator == '.AND.':
                    self.position += 5
                    return Lexem.CLASS_AND
                self.value = '.'
                self.position += 1
                return Lexem.CLASS_UNKNOWN

            if self.content[self.position:self.position + 3] == 'Var' and not self.content[self.position + 3:self.position + 4].isalpha():
                self.position += 3
                return Lexem.CLASS_VAR_WORD
            if self.content[self.position:self.position + 5] == 'Begin' and not self.content[self.position + 5:self.position + 6].isalpha():
                self.position += 5
                return Lexem.CLASS_BEGIN_WORD
            if self.content[self.position:self.position + 3] == 'End' and not self.content[self.position + 3:self.position + 4].isalpha():
                self.position += 3
                return Lexem.CLASS_END_WORD
            if self.content[self.position:self.position + 7] == 'Boolean' and not self.content[self.position + 7:self.position + 8].isalpha():
                self.position += 7
                return Lexem.CLASS_BOOLEAN_WORD

            if c in [' ', '\n', '\r', '\t']:
                if c == '\n':
                    self.code_line += 1
                self.position += 1
                # print("whitespace...[", c, "]")
                continue

            # read until whitespaces
            p = self.position
            buf = None
            while True:
                p += 1
                buf = self.content[self.position:p]
                if buf[-1:] in list(' \n\r\t,;=():01.'):
                    self.position = p - 1
                    self.value = buf[0:-1]
                    break
                if len(buf) != p - self.position:
                    # print("eof while read unknown token", p, self.position, buf)
                    self.position = p
                    self.value = buf
                    break
            if buf is not None:
                if self.value.islower() and self.value.isalpha():
                    return Lexem.CLASS_IDENTIFIER
                return Lexem.CLASS_UNKNOWN

    def run(self):
        fileName = 'input.txt'
        if len(sys.argv) > 1:
            fileName = sys.argv[1]
        print("Reading code from " + fileName + "...")
        self.content = open(fileName, 'r').read(100000)

        outFileName = 'lexemes.txt'
        fOutput = open(outFileName, "w")
        while True:
            l = self.next_token()
            output = str(self.code_line) + "\t" + l.name
            if self.value is not None:
                output += "\t" + self.value
            else:
                output += "\t" + l.get_view()
            fOutput.write(output + "\n")
            if l is Lexem.CLASS_NULL:
                break
        fOutput.close()


parser = Parser()
parser.run()


class SyntaxChecker(object):
    cur_pos = 0
    allowed_variables = []
    assigned_variables = []
    lexems = []

    def err(self, data, description):
        print("Syntax error in line " + str(data[0]) + ": " + description)
        print("L" + str(data[0]) + " >" + data[1].name + " (" + data[2] + ")")
        sys.exit(1)


    def cur_lexem(self):
        return self.lexems[self.cur_pos]


    def next_lexem(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.lexems):
            self.err(self.lexems[self.cur_pos - 1], "Unexpected end")
        return self.lexems[self.cur_pos]


    def is_cur_lexem_type(self, type):
        return self.cur_lexem()[1] is type


    def expect(self, type, description='Unexpected token (?)', auto_next_lexem=True):
        if self.cur_lexem()[1] is not type:
            self.err(self.cur_lexem(), description)
        if auto_next_lexem:
            self.next_lexem()


    def check_subexpr(self):
        if self.is_cur_lexem_type(Lexem.CLASS_LBRACKET):
            self.next_lexem()
            self.check_expression()
            self.expect(Lexem.CLASS_RBRACKET, "Expected ')'")
        elif self.is_cur_lexem_type(Lexem.CLASS_ZERO) or self.is_cur_lexem_type(Lexem.CLASS_ONE):
            self.next_lexem()
        elif self.is_cur_lexem_type(Lexem.CLASS_IDENTIFIER):
            var = self.cur_lexem()[2]
            if not var in self.allowed_variables:
                self.err(self.cur_lexem(), "Undefined variable")
            if not var in self.assigned_variables:
                self.err(self.cur_lexem(), "Unassigned variable")
            self.next_lexem()
        else:
            self.err(self.cur_lexem(), "Expected subexpression: (expr) | 0 | 1 | variable")
        if self.cur_lexem()[1] in [Lexem.CLASS_AND, Lexem.CLASS_XOR, Lexem.CLASS_OR]:
            self.next_lexem()
            self.check_subexpr()


    def check_expression(self):
        if self.is_cur_lexem_type(Lexem.CLASS_NOT):
            self.next_lexem()
        self.check_subexpr()


    def check_assignment(self):
        self.expect(Lexem.CLASS_IDENTIFIER, "Expected variable", auto_next_lexem=False)
        var = self.cur_lexem()[2]
        if not var in self.allowed_variables:
            self.err(self.cur_lexem(), "Undefined variable")
        self.next_lexem()
        self.expect(Lexem.CLASS_EQUAL, "Expected '='")
        self.check_expression()
        self.expect(Lexem.CLASS_SEMICOLON, "Expected ';'")
        self.assigned_variables.append(var)

    def load(self):
        fInput = open('lexemes.txt', 'r')
        for line in fInput:
            lnumber, type, value = line.replace("\n", "").split("\t")
            row = [int(lnumber), Lexem[type], value]
            self.lexems.append(row)
            if row[1] is Lexem.CLASS_UNKNOWN:
                self.err(row, "Unknown token")

    def run(self):
        self.load()

        self.expect(Lexem.CLASS_VAR_WORD, "Expected 'Var'")
        while True:
            self.expect(Lexem.CLASS_IDENTIFIER, "Expected variable name", auto_next_lexem=False)
            self.allowed_variables.append(self.cur_lexem()[2])
            self.next_lexem()
            if self.is_cur_lexem_type(Lexem.CLASS_COMMA):
                self.next_lexem()
                continue
            if self.is_cur_lexem_type(Lexem.CLASS_COLON):
                self.next_lexem()
                break
            self.err(self.cur_lexem(), "Expected comma or colon")
        self.expect(Lexem.CLASS_BOOLEAN_WORD, "Expected 'Boolean'")
        self.expect(Lexem.CLASS_SEMICOLON, "Expected semicolon")
        self.expect(Lexem.CLASS_BEGIN_WORD, "Expected 'Begin'")

        while self.is_cur_lexem_type(Lexem.CLASS_IDENTIFIER):
            self.check_assignment()

        self.expect(Lexem.CLASS_END_WORD, "Unexpected 'End'")
        if self.cur_pos != len(self.lexems) - 1:
            self.err(self.cur_lexem(), "Expected program end")

        print("Syntax checking successfully finished.")


checker = SyntaxChecker()
checker.run()


class PostfixWriter(SyntaxChecker):
    stack = []
    fOut = None

    def write_lexem(self, type):
        if type is not None:
            self.expect(type, auto_next_lexem=False)
        self.fOut.write(self.cur_lexem()[2])
        if not self.is_cur_lexem_type(Lexem.CLASS_IDENTIFIER):
            self.fOut.write(" ")
        if self.is_cur_lexem_type(Lexem.CLASS_SEMICOLON) or self.is_cur_lexem_type(Lexem.CLASS_BEGIN_WORD):
            self.fOut.write("\n")
        self.next_lexem()


    def process_subexpr(self):
        my_stack = []
        if self.is_cur_lexem_type(Lexem.CLASS_LBRACKET):
            self.next_lexem()
            my_stack.extend(self.process_expression())
            self.expect(Lexem.CLASS_RBRACKET)
        elif self.is_cur_lexem_type(Lexem.CLASS_ZERO) or self.is_cur_lexem_type(Lexem.CLASS_ONE):
            my_stack.append(self.cur_lexem()[2])
            self.next_lexem()
        elif self.is_cur_lexem_type(Lexem.CLASS_IDENTIFIER):
            var = self.cur_lexem()[2]
            my_stack.append(self.cur_lexem()[2])
            self.next_lexem()
        else:
            self.err(self.cur_lexem(), "Expected subexpression: (expr) | 0 | 1 | variable")
        if self.cur_lexem()[1] in [Lexem.CLASS_AND, Lexem.CLASS_XOR, Lexem.CLASS_OR]:
            my_stack.insert(0, self.cur_lexem()[2])
            self.next_lexem()
            my_stack.extend(self.process_subexpr())
        return my_stack

    def process_expression(self):
        my_stack = []
        if self.is_cur_lexem_type(Lexem.CLASS_NOT):
            my_stack.append(Lexem.CLASS_NOT.get_view())
            self.next_lexem()
        my_stack.extend(self.process_subexpr())
        return my_stack

    def process_assignment(self):
        var = self.cur_lexem()[2]
        self.next_lexem()
        self.expect(Lexem.CLASS_EQUAL)
        self.stack.append(Lexem.CLASS_EQUAL.get_view())
        self.stack.extend(self.process_expression())
        self.stack.append(var)

        self.expect(Lexem.CLASS_SEMICOLON)

    def dump_stack(self):
        for var in reversed(self.stack):
            self.fOut.write(var + " ")
        self.fOut.write("\n")
        self.stack = []
        pass

    def run(self):
        self.load()

        self.fOut = open('postfix.txt', 'w')
        self.stack = []
        while not self.is_cur_lexem_type(Lexem.CLASS_SEMICOLON):
            self.write_lexem(None)
        self.write_lexem(Lexem.CLASS_SEMICOLON)
        self.write_lexem(Lexem.CLASS_BEGIN_WORD)

        while self.is_cur_lexem_type(Lexem.CLASS_IDENTIFIER):
            self.process_assignment()
            self.dump_stack()

        self.write_lexem(Lexem.CLASS_END_WORD)
        self.fOut.close()
        print("Postfix notation was written successfully.")


writer = PostfixWriter()
writer.run()


class Generator(object):
    f = None
    params = []
    instr = []

    def process(self, line):
        tokens = line.strip().split(" ")
        out_var = tokens[0]
        for i in range(1, len(tokens) - 1):
            if tokens[i] in ['1', '0']:
                self.instr.append("LIT " + tokens[i])
            elif tokens[i] in ['.NOT.', '.AND.', '.OR.', '.XOR.']:
                self.instr.append(tokens[i].replace(".", ""))
            elif tokens[i].isalpha():
                self.instr.append("LOAD " + str(self.params.index(tokens[i])))
            else:
                print("Unexpected token: " + tokens[i])
        self.instr.append("STO " + str(self.params.index(out_var)))

    def run(self):
        f = open('postfix.txt', 'r')
        lines = []
        for l in f:
            lines.append(l.replace("\n", ""))
        self.params = re.split("\\s+", lines[0].replace(",", "").replace(":", "").replace(";", "").strip())[:-1]
        for i in range(2, len(lines) - 1):
            self.process(lines[i])
        out = open('asm.txt', 'w')
        for code in self.instr:
            out.write(code + "\n")
        out.close()
        print("ASM code was written successfully!")

generator = Generator()
generator.run()