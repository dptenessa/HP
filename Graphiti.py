import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import os

def graphiti():
    print("Preparing your pdf file... This will take less than a minute.")
    FLAT = 999999
    font = {
            'size': 5,
            }
    plt.rc('font', **font)
    excel_wrkbook = "Recommended prices.xlsx"     # "HS HT.xlsx"
    df = pd.read_excel(excel_wrkbook)
    df = df.loc[((df.Company == "A1") | (df.Company == "T")) & (df["Tariff Name"] != "PRP")]
    iterations = df[['Manufacturer', 'Model', 'Memory']].copy()
    iterations.drop_duplicates(inplace=True)
    pdf_file=excel_wrkbook+".pdf"
    with PdfPages(pdf_file) as pdf:
        for index, row in iterations.iterrows():
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
            fig.suptitle(row[0]+" "+row[1]+" "+row[2])
            dfa1 = df.loc[((df.Company == "A1")) & (df.Manufacturer == row[0]) & (df["Model"] == row[1]) & (df.Memory == row[2])].copy()
            dfa1.sort_values(by=['GB'], inplace=True)
            xa1 = dfa1.GB
            mrc_a1 = dfa1.MRC_total
            handset_a1 = dfa1["Final HS price"]
            dfT = df.loc[((df.Company == "T")) & (df.Manufacturer == row[0]) & (df["Model"] == row[1]) & (df.Memory == row[2])].copy()
            dfT.sort_values(by=['GB'], inplace=True)
            xT = dfT.GB
            mrc_T = dfT.MRC_total
            handset_T = dfT["Final HS price"]
            ax1.plot(xa1, mrc_a1,marker=11,color="r")
            ax1.plot(xT, mrc_T,marker=10,color="m")
            ax1.set_title("MRCs")
            ax2.plot(xa1, handset_a1,marker=11,color="r")
            ax2.plot(xT, handset_T,marker=10,color="m")
            ax2.set_title("HS prices")
            ax3.plot(mrc_a1, handset_a1,marker=11,color="r")
            ax3.scatter(mrc_T, handset_T,marker=10,color="m")
            ax3.set_title("HS prices")
            #ax1.semilogx(FLAT, np.exp(-FLAT / 5.0))
            #ax2.semilogx(FLAT, np.exp(-FLAT / 5.0))
            ax1.legend(['MRC A1','MRC T'])
            ax2.legend(['HS price A1', 'HS price T'])
            ax3.legend(['HS price A1', 'HS price T'])
            for i, dot in dfT.iterrows():
                txt1 = (dot["Tariff Name"] + " " + str(dot["MRC_total"]))
                txt2 = (dot["Tariff Name"] + " " + str(dot["Final HS price"]))
                ax1.text(xT[i], mrc_T[i], txt1,horizontalalignment='center',)
                ax2.text(xT[i],handset_T[i],txt2,horizontalalignment='right',)
                ax3.text(mrc_T[i],handset_T[i],txt2,horizontalalignment='left',)
            #plt.show()
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
        d = pdf.infodict()
        d['Title'] = 'MRCs and HS prices comparison'
        d['Author'] = u'Diego Perez-Tenessa'
        d['Subject'] = 'MRCs and HS prices comparison'
        d['Keywords'] = 'MRC HS prices handset comparison'
        d['CreationDate'] = datetime.datetime(2009, 11, 13)
        d['ModDate'] = datetime.datetime.today()
        print("Ready!")
        os.startfile(pdf_file, operation='open')

#graphiti()