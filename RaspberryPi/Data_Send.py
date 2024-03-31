import serial


def main():
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    # params to send to Raspberry Pi
    data_send = input("send data?")
    curr_date = 12
    curr_time = 59
    sample_time = 32
    minimum_percent_outside_air = 12
    return_air_temp = 13
    low_lockout_temp = 15
    high_lockout_temp = 17
    ideal_mat = 16
    params = [curr_date, curr_time, sample_time, minimum_percent_outside_air, return_air_temp, low_lockout_temp, high_lockout_temp, ideal_mat, params]
    for param in params:
        string = b"{}\n".format(param)
        print(string)
        ser.write(string)


if __name__ == '__main__':
    main()