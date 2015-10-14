import lpt.lfp.lfp as lfp


def read_ifp(file_name):
    print('Loading IFP or IFR file: ' + file_name)
    loaded = lfp.Lfp(path=file_name)
    print(loaded)
    print('Finished Loading.')
