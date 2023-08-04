#INPUT FILES
FILE_LL = "ll.txt"
FILE_LR = "lr.txt"
FILE_INPUT = "input.txt"

LL_str = []
LL_stack = []
LL_input = []
LL_action = []
LL_output = []

LR_str = []
LR_input_word = ''

LR_state = []
state = []
Lr_counter = 1
current = ""
arrow = 0

inputFile = open(FILE_INPUT, "r")
input = inputFile.read()

inputFileLL = open(FILE_LL, "r")
inputLL = inputFileLL.read()

inputFileLR = open(FILE_LR, "r")
inputLR = inputFileLR.read()

#create the dictionary for the left most derivation from the LL file
dictLL = {}
global derivation_LL   #the first row of the table for  the dictionary keys
global actions 

start_LL = inputLL.splitlines()[1].replace(" ","").split(";")[0]
def createLLTable():
    first_line = True
    actions = []
    for line in inputLL.splitlines():
        lines = line.replace(" ","").split(";")
        if first_line == True:
            derivation_LL = lines[1:] #the first index contains the derivation type like "LL" and we do not need this.
            #print(str(derivation_LL))
            first_line = False
        else:
            for i in range(len(derivation_LL)):
                # create the dictionary part: {id: {E: E->TA}, *: {E: E->TA}}
                try:
                    dictLL.setdefault(derivation_LL[i], {})[lines[0]] = lines[i+1].split("->")[1] 
                    if lines[0] not in actions:
                        actions.append(lines[0])
                except: #for empty places
                    continue
    return derivation_LL, actions



def getNextTerminal(str, terminals): #get id from the id+id*id
    terminal = ""
    for chr in str:
        terminal = terminal + chr
        if terminal in terminals:
            return terminal
    return ""


def getNextAction(str, actions, terminals): #get T from the TA
    action = ""
    is_valid = False
    terminal = getNextTerminal(str, terminals)
    if terminal!="":
        is_valid = True
    str = str[len(terminal):]
    #print(str)
    for chr in str:
        action = action + chr
        if action in actions:
            return action, is_valid
    return "", is_valid

def reverseStr(stack_str, terminals, except_char):
    output = ""
    key = ""
    for ch in stack_str:
        if ch.isupper():
            if key=="":
                output = str(ch + output)
            elif key in terminals:
                output = str(key + output)
                output = str(ch + output)
                key = ""
        else:
            key = str(key + ch)
            if key in terminals:
                output = str(key + output)
                key = ""
    return str(except_char + output)

#returns output of the left most derivation process
def leftDerivation(input_str):
    #clear all lists
    LL_action = []
    LL_input = []
    LL_stack = []
    print("\nThe given input is {}".format(input_str))
    print("\nRead LL(1) parsing table from file ", FILE_LL)


    terminals = createLLTable()[0] #id, +, * etc. 
    actions = createLLTable()[1] #E, A, T etc.
    first_terminal = getNextTerminal(input_str, terminals)
    first_action = actions[0]

    current_key = first_terminal
    current_term = first_action
    current_input = input_str
    
    # ADD FIRST VALUES TO STACKS
    LL_stack.append(terminals[-1])
    LL_input.append(current_input)

    bound = 50 #if the derivation contains more than bound state than reject the operation
    matched = ""
    while(current_term!=""):

        is_valid_key = getNextAction(current_term, actions, terminals)[1]
        if is_valid_key: # if we catch the terminal from input for example idBA change the currentkey
            current_input = current_input[len(current_key):]
            current_term = current_term[len(current_key):]
            matched = current_key
            current_key = getNextTerminal(current_input, terminals)



        action_key = getNextAction(current_term, actions, terminals)[0] # its equal to E for the first term
        try:
            action = dictLL[current_key][action_key] # its equal to TA for the first iteration
        except:
            LL_action.append(str("REJECTED   (" + action_key + " does not have an action/step for " + current_key + ")"))
            break

        if not is_valid_key:
            current_term = str(action + current_term[len(action_key):] )
     

        if current_term[0] == "ϵ":
            current_term = current_term.replace("ϵ", "")

        stack_str = reverseStr(current_term, terminals, terminals[-1])
        LL_input.append(current_input)
        LL_stack.append(stack_str)

        if is_valid_key:
            LL_action.append(str("Match and remove " + matched))
        else:
            LL_action.append(str(action_key + "->" + action))

        if bound<1:
            LL_input.append(current_input)
            LL_stack.append(stack_str)
            LL_action.append("REJECT")
  
    if bound>1 and "REJECT" not in LL_action[-1]:#ADD THE LAST STATE
            LL_input.append(terminals[-1])
            LL_stack.append(terminals[-1])
            LL_action.append("ACCEPT")

    print()
    print("-"*70)
    print("{:<5} {:<10} {:<15} {:<20}".format("No", "| State", "| Input", "| Stack"))
    print("-"*70)
    for i in range(len(LL_action)):
        print("{:<5} {:<10} {:<15} {:<20}".format(i+1, LL_stack[i], LL_input[i], LL_action[i]))
    print("-"*70)

        
        




#////////////////////////////////////////////LR///////////////////////////////////

def create_LR_Matrix():
    rows = inputLR.strip().split('\n')
    columns = rows[0].split(';')
    matrix = []
    matrix.append(columns)
    for row in rows[1:]:
        data = row.split(';')
        for i in range(len(data)):
            if data[i].startswith("State_"):
                state_num = int(data[i].split("_")[1])
                data[i] = state_num
            elif data[i].strip().isspace():
                data[i] = ''
            else:
                if ' ' in data[i]:
                    data[i] = data[i].replace(' ', '')
                try:
                    data[i] = int(data[i])
                except ValueError:
                    try:
                        data[i] = float(data[i])
                    except ValueError:
                        pass
        matrix.append(data)
    return matrix


def rightDerivation(matrix, LR_read_string):
    print("Read LR(1) parsing table from file  lr.txt")
    i = 2
    j = 1
    LR_read = []
    LR_counter = 0
    LR_input_word = LR_read_string
    global arrow
    global Lr_counter
    global state
    global stri
    global current
    flag = False
    state = []
    stri = ""
    current = ""
    arrow = 0
    lr = True
    Lr_counter = 1
    print("\nThe given input is {}".format(LR_input_word))
    print("")
    while(lr):
        if(str(matrix[i][j]).isnumeric()):
            for x in range(len(matrix[1])):
                if (flag or matrix[1][x] == LR_input_word[LR_counter]):
                    if(flag):
                        current = matrix[1][j]
                        klm = "Shift to state " + str(matrix[i][j])
                        LR_output(current,LR_read_string,not flag,klm)
                        ltr = LR_read[len(LR_read) - 1]
                        i = matrix[i][j] + 1
                        for n in range(len(matrix[1])):
                            if(ltr == matrix[1][n]):
                                j = n
                                break

                    elif not flag or matrix[1][x] != LR_input_word[LR_counter]:
                        state.append(matrix[i][0])
                        new_state = state.copy()  # or new_state = state[:]
                        LR_state.append(new_state)
                        current = matrix[1][x]
                        LR_read.append(matrix[1][x])
                        if not str(matrix[i][x]).isnumeric() and not "->" in str(matrix[i][x]):
                            lr = False
                            klm = "REJECTED   (State {} does not have an action/step for {})".format(matrix[i][0],matrix[1][x])
                            LR_output(current, LR_read_string, flag, klm)
                            break
                        klm = "Shift to state " + str(matrix[i][x])
                        i = matrix[i][x] + 1
                        for c in range(len(matrix[1])):
                            if (matrix[1][c] == LR_input_word[LR_counter + 1]):
                                j = c
                                break
                        LR_output(current,LR_read_string,flag,klm)
                    break
            LR_counter += 1

        elif "->" in str(matrix[i][j]):
            state.append(matrix[i][0])
            new_state = state.copy()  # or new_state = state[:]
            LR_state.append(new_state)
            if flag:
                flag = False #if we went through a state that included -> before
            else:
                LR_read.append(matrix[1][j])
            current = matrix[1][j]
            klm = "Reverse " + str(matrix[i][j])
            LR_output(current, LR_read_string, flag, klm)

            LR_read_string = ''.join(LR_read)
            stri = str(matrix[i][j]).split("->")
            current = stri[0]
            if LR_read_string.__contains__(stri[1]):
                LR_read = []
                LR_read_string = LR_read_string.replace(stri[1],stri[0])
                for y in range(len(LR_read_string)):
                   LR_read.append(LR_read_string[y])
            for x in range(len(matrix[1])):
                if(current == matrix[1][x]):
                    j = x
                    break
            state = state[:-len(stri[1])]
            new_state = state.copy()
            LR_state.append(new_state)
            arr = LR_state[len(LR_state) - 1]
            i = arr[len(arr) - 1] + 1
            LR_counter += 1
            flag = True#if there was a state before that had a ->
            arrow += 1
        else:
            if(matrix[i][j].upper() == "ACCEPT"):
                flag = False
                current = matrix[1][j]
                state.append(matrix[i][0])
                new_state = state.copy()
                LR_state.append(new_state)
                LR_output(current,LR_read_string,flag,"ACCEPT")
                break
            else:
                current = matrix[1][j]
                state.append(matrix[i][0])
                new_state = state.copy()
                LR_state.append(new_state)
                LR_output(current, LR_read_string, flag, "REJECT")
                break



def LR_output(current,LR_read_string,flag,klm):
    global Lr_counter
    global arrow
    if(Lr_counter == 1):
        print("Processing input string {} for LR(1) parsing table.".format(LR_input_word))
        print("NO | STATE STACK  | READ  | INPUT | ACTION")
    if(flag):
        print("{:<3}| {:<12} | {:<5} | {:<5} | {}".format(str(Lr_counter), str(LR_state[Lr_counter - 1 - arrow]), current or '', LR_read_string, klm))
    else:
        print("{:<3}| {:<12} | {:<5} | {:<5} | {}".format(str(Lr_counter), str(LR_state[Lr_counter - 1]), current or '', LR_read_string, klm))

    Lr_counter += 1


print("Read input strings from file ", FILE_INPUT)
for line in input.splitlines():
    lines = line.replace(" ","").split(";")

    if lines[0] == "LL":
        LL_output = leftDerivation(lines[1])

    elif lines[0] == "LR":
        print()
        matrix = create_LR_Matrix()
        rightDerivation(matrix, lines[1])
        print()
    else:
        continue


