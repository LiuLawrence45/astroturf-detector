import threading 
import time 

counter = 0

def walk_dog(first_name, last_name): 
    global counter # need this to be able to change the value.
    # time.sleep(8)
    for _ in range(1000):
        counter+=1
        time.sleep(0.0001)
    print(f"You finish walking the dog: {first_name}")
    
    
    
def take_out_trash():
    global counter
    # time.sleep(2)
    for _ in range(1000):
        counter+=1
        time.sleep(0.0001)
    print("You finish taking out the trash")
    
    
    
def get_mail():
    global counter
    # time.sleep(3)
    for _ in range(1000):
        counter+=1
        time.sleep(0.0001)
    print("You finish getting the mail")
    
if __name__ == "__main__":
    chore1 = threading.Thread(target=walk_dog, args=("Your mom", "your dad"))
    chore1.start()
    chore2 = threading.Thread(target=take_out_trash)
    chore2.start()
    chore3 = threading.Thread(target=get_mail)
    chore3.start()
    
    chore1.join()
    chore2.join()
    chore3.join()
    
    print(f"All tasks finished. Counter is: {counter}")
    
    
