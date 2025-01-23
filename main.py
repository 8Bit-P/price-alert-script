def main():
    print("working")

    #1. Parse json to object

    #2. Access webpage and get data in the html element designated by priceTagId or priceTagClass, whichever is there

    #3. Check for all the objects if any of the prices has dropped below priceBelowAlert

    #4. If yes, send an email to the user with the link to the product and the amount of price drop
        #4.1 If email has been sent with alert, store value in local file to avoid sending multiple emails for the same product
        #4.2 If price rises again above the threshold, remove the entry from the local file

    #5. Wait "rerunIntervalHours" hours and repeat the process
    

if __name__ == "__main__":
    main()