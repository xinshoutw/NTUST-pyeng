from lib.FormSubmitter import FormSubmitter


class UserData:
    ...  # TODO: implement user data class


def main():
    # use TARGET_URL=https://lc.ntust.edu.tw/p/403-1070-1828-1.php?Lang=zh-tw to find all available form,
    # list all for user to choose, user can choose one or many of them

    # use FormSubmiter to brute force every form and submit the answer by user data list
    # print answer of each form
    # print the result of each user of each form, get 1 screenshot of each result by using the browser (only the top part of the webpage needs to be screenshoted)


    br = FormSubmitter(
        url="https://forms.gle/wwVThW5wQKABwXfC7",
        ignore_out_bounded=True
    )

    # br.set_answer({'entry.1000665440': 'labeled', 'entry.958025575': ' ', 'entry.132481896': ' ', 'entry.674183365': ' ', 'entry.1415839849': ' ', 'entry.1666530282': ' ', 'pageHistory': '0,1', 'entry.1481666631': 'overall', 'entry.602868708': 'prior', 'entry.111117338': 'implications', 'entry.2103165715': 'unresolved', 'entry.1769495573': 'ethnic', 'entry.800097361': 'commitment', 'entry.1972244970': 'label', 'entry.1631731926': 'retained', 'entry.2101415341': 'sum', 'entry.884589525': 'debate', 'entry.2031939485': 'principal', 'entry.614446191': 'output', 'entry.1024607664': 'erroneous', 'entry.1878398158': 'annual', 'entry.50658700': 'cycle', 'entry.818640596': 'subsequent', 'entry.426771950': 'apparent', 'entry.548194065': 'job', 'entry.527340659': 'implemented'})
    # br.set_answer_url(
    #     "https://docs.google.com/forms/d/e/1FAIpQLScBiwM2awUdfp9OCXauD5xS7R9l0qgOFuWUC-s0_seTWvsr3A/viewscore?viewscore=AE0zAgCBuDCem0YmiwGPoD_47txki-t-HEwvqrU9yCbafX3rE2I9RKj_3H_zYhfOS1fsUaU")
    br.print_answer_web()
    br.print_answer_dict()


    br.auto_submit(
        indicate_mapper={
            ("姓名", "名字 / Name",): "黃宥維",
            ("科系 / Department",): "四資工一",
            ("學號", "學號 / Student ID"): "B11315009",
            ("系所／單位 Department",): "資訊工程系(所) Department of Computer Science & Information Engineering",
            ("E-mail", "Email", "電子郵件 / E-mail",): "contact@xinshou.tw",
            ("手機號碼",): "0916910404",
            ("測驗動機 (修讀整合式英語課程之同學請務必填寫正確)",): "CC106B023 整合式學術英語(下) 蔡郁瑄(W1,W2)",
            ("測驗動機",): "CC106B023 整合式學術英語(下) 蔡郁瑄(W1,W2)",
        },
        keyword_mapper={

        },
    )

    br.auto_submit(
        indicate_mapper={
            ("姓名", "名字 / Name",): "吳思澄",
            ("科系 / Department",): "四電子一丙",
            ("學號", "學號 / Student ID"): "B11302242",
            ("系所／單位 Department",): "電子工程系(所) Department of Electronic & Computer Engineering",
            ("E-mail", "Email", "電子郵件 / E-mail",): "qqritaqq@gmail.com",
            ("手機號碼",): "0905075273",
            ("測驗動機 (修讀整合式英語課程之同學請務必填寫正確)",): "參加自學點數活動",
            ("測驗動機",): "參加自學點數活動",
        },
        keyword_mapper={

        },
    )


if __name__ == '__main__':
    main()
