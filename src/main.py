from codegen.codegen import CodeGenerator


def show_copyright():
    print('main()')


def main():
    # show copyright
    show_copyright()

    # process cmd args

    # init code generator
    code_gen = CodeGenerator()

    # generate files
    code_gen.generate_cpp('hello.yaml', 'result')

    # print results
    pass


if __name__ == "__main__":
    main()