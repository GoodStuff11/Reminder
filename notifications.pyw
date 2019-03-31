from win10toast import ToastNotifier

# convert this to .exe file so that console doesnt need to be opened
toaster = ToastNotifier()
toaster.show_toast("Reminder", "Do your work!", duration=10)
