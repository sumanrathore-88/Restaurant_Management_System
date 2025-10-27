

from authentication import registration as reg

def main():
    while True:
        print("\n==== CHATORA RESTAURANT MANAGEMENT ====")
        print("1. Sign In")
        print("2. Sign Up (Register Staff)")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            try:
                reg.staff_sign_in_flow()
            except Exception as e:
                print("Sign-in failed:", e)

        elif choice == "2":
            try:
                reg.register_staff_interactive()
            except Exception as e:
                print("Registration failed:", e)

        elif choice == "3":
            print("Exiting... Thank you for visiting CHATORA!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
