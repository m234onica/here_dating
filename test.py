from src.route import api
from async import run
if __name__ == "__main__":
    head = pow(10, 16)
    trail = head + 1000
    userId_list = [str(s) for s in range(head, trail)]
    for userId in userId_list:
        print("hi")
        api.pair_user("2322", userId)
    run.main()