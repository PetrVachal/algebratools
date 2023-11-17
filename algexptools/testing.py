from algexptools import AlgExp, NumericAlgExp, VariableAlgExp

if __name__ == '__main__':
    while True:
        alg_exp_input: str = input(": ")
        if alg_exp_input == "exit":
            break
        try:
            alg_exp: AlgExp = AlgExp.initializer(alg_exp_input)
            print(f"exp: {alg_exp}")
            print(f"type: {alg_exp.__class__.__name__}")
            if isinstance(alg_exp, NumericAlgExp):
                print(f"value: {alg_exp.value}")
            elif isinstance(alg_exp, VariableAlgExp):
                print(f"variables: {alg_exp.variables}")
                print(f"variables_domains: {alg_exp.variables_domains}")
                print(f"immutable_contents: {alg_exp.immutable_contents}")
        except (AssertionError, ValueError) as err:
            print(err)
