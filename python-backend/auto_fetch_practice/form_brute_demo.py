from lib.FormSubmitter import FormSubmitter


def main():
    br = FormSubmitter(
        url="https://docs.google.com/forms/d/e/1FAIpQLScuSOFqmXlfxnzwpC78REM5pXc9-me7bAz_4hmab1wtgEZaCw/viewform?usp=header",
        ignore_out_bounded=True
    )
    # br.set_answer()
    # br.set_answer_url("")
    br.print_answer_web()
    br.print_answer_dict()

    br.auto_submit(
        indicate_mapper={
            ("學號", "學號 / Student ID"): "A12345678",
            ("姓名", "名字 / Name",): "張小明",
            ("科系 / Department",): "四三十二",
            ("系所／單位 Department",): "電子工程系(所)",
            ("Email", "電子郵件 / E-mail",): "contact@me.tw",
            ("手機號碼",): "0912345678",
        },
        keyword_mapper={
            ("測驗動機",): "CC105B000"
        },
    )


if __name__ == '__main__':
    main()
