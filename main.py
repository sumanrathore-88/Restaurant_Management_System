from authentication.registration import register_staff, staff_login, staff_menu_loop


def main():
    print('Welcome to chatora_restaurant')
    while True:
        print('\n1. Register Staff  2. Staff Login  3. Exit')
        choice = input('Choose: ').strip()
        if choice == '1':
            register_staff()
        elif choice == '2':
            sid = staff_login()
            if sid is not None:
                staff_menu_loop(sid)
        elif choice == '3':
            print('Goodbye')
            break
        else:
            print('Invalid option')


if __name__ == '__main__':
    main()
