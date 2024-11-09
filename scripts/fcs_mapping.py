from share.misc import load_csv

if __name__ == '__main__':
    for row in load_csv('./tmp/fcs_mapping.csv'):
        if row[4] != ' ':
            #print(row)
            print(f'/usr/ios/cli/ioscli vfcmap -vadapter {row[0]} -fcp {row[4]};')




