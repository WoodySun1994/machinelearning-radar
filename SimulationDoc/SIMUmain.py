import SimuGen

def main():
    SD = SimuGen.SimuData(autotesten = True)
    SD.create_simu()
    SD.save_simu()
    SD.show_simu()


if __name__ == "__main__":
    main()
