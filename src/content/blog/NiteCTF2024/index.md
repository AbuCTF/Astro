---
title: NiteCTF 2024
tags:
- Writeups
date: Dec 18 2024
summary: Challenges from NiteCTF
draft: false
---
Even though I wasn’t able to attend this fantastic CTF, I’ll try my hand in solving these really well-crafted challenges. Props to the `Cryptonite` team and all the challenge creators.

```bash
Author: Abu
```

## Hardware

![1](./1.png)

Starting-off with Hardware cause why not LOL.

You know the feeling when you’re put in a place, where you pretty much have no clue what was going on, that was me when doing these hardware challenges.

![2](./2.png)

明日も続きます。

### **U ARe T Detective**

**Author(s)**: `vikaran`

**Description**: One of our Detective tapped a channel to intercept this signal but couldn't read it, HELP HIM

Given: `signal.sr`

As the challenge name suggests, it has something to do with UART.

💡 UART stands for **universal asynchronous receiver / transmitter** and is a simple, two-wire protocol for exchanging serial data.

![4](./4.png)

Notice the peculiar `.sr` file format, googling that leads us to `Sigrok`. Another way is to extract the file and read the metadata inside.

```bash
[global]
sigrok version=0.6.0-git-b503d24

[device 1]
capturefile=logic-1
total probes=8
samplerate=16 MHz
total analog=0
probe1=D0
probe2=D1
probe3=D2
probe4=D3
probe5=D4
probe6=D5
probe7=D6
probe8=D7
unitsize=1
```

When installing `Sigrok`, faced this error.

```bash
Sigrok.Pulseview MSVCR100.dll missing error
```

[microsoft/winget-pkgs/issues/92844](https://github.com/microsoft/winget-pkgs/issues/92844)

![5](./5.png)

That fixes the issue. Opening up the file in Sigrok Pulse Viewer.

![6](./6.png)

We notice strange markings in the `D1` pane, on closer notice these look like bits.

![7](./7.png)

Now, we look to find the baud rate of the channels.

💡 Baud rate is **the measure of the number of changes to the signal (per second) that propagate through a transmission medium**.

In order to find the baud rate, you need to find the time taken for the smallest bit, then reciprocal it to find the custom baud rate, which is then used for decoding the UART signal.

[Decode/Analyse the following UART signals](https://electronics.stackexchange.com/questions/501849/decode-analyse-the-following-uart-signals)

As I looked into the official write-up, which is extremely small, the intended way was to find the custom baud rate and try to UART decode it. but it’s easier to do this manually (at least for me).

We need to do a bit of reverse thinking in order to recognize the bits, as you can see, there are segments of these square waveforms throughout the D1 pane, and each segment can be considered as a byte, to split the byte into the individual bits, we count the number of samples in the entire byte and divide it by 9 (since the starting byte is also considered), when we count the number of samples (these are the dots you see across the segment), we count up to 27, dividing by 9, we get 3. Therefore, we represent every bit with 3 samples, I donno if it’s twisted logic, but it satisfies mine HAHA. 

![3](./3.png)

In the first segment, we receive a byte code of `01110110` and since UART transmits data from LSB to MSB, we reverse the code, giving us an output of `01101110`.

```bash
└─$ python3
Python 3.12.7 (main, Nov  8 2024, 17:55:36) [GCC 14.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> binary = '01101110'
>>> decimal = int(binary, 2)
>>> ascii = chr(decimal)
>>> print(ascii)
n
```

That gives us the first character of the flag. Doing the same for all the segments.

```bash
>>> binary = ('01101110','01101001','01110100','01100101', '01111011','01101110','00110000','01101110','01011111','01110011','01110100','01100100','01011111','01100010','00110100','01110101','01100100','01011111','01110010','00110100','01110100','00110011','01110011','01011111','01100110','01110100', '01110111', '01111101')
>>> convert = [chr(int(b, 2)) for b in binary]
>>> ascii = ''.join(convert)
>>> print(ascii)
nite{n0n_std_b4ud_r4t3s_ftw}
```

Flag: `nite{n0n_std_b4ud_r4t3s_ftw}`

### **Ancient Ahh Display**

**Author(s)**: `xenon`

**Description**: bro is still stuck on Basys 3 Artix-7's display, LOL!

**Given**: `display.txt & fpga_inputs.xlsx`

Before we dive into this challenge, there’s a lot of pre-learning to do. I’ll list down the important concepts.

💡 The **Basys 3 Artix-7 FPGA** is a development board that is designed for learning and experimentation with Field-Programmable Gate Arrays (FPGAs). It is powered by the **Xilinx Artix-7 FPGA** and provides an accessible platform for those interested in digital design, hardware development, and embedded systems.

The Basys 3 is aimed at educational use, and many students and professionals use it to learn about FPGA design, digital circuits, and embedded systems.

- The Artix-7 FPGA offers a rich set of programmable logic resources, including **LUTs (Look-Up Tables)**, **DSP slices** for signal processing, and **block RAM** for memory storage.
- It supports a variety of **high-speed serial interfaces** such as **SPI**, **I2C**, **UART**, and **USB**.

In summary, the **Basys 3 Artix-7 FPGA** is a powerful and versatile development board that allows users to design and implement custom digital circuits using the Xilinx Artix-7 FPGA. It is commonly used for educational purposes, offering a range of I/O components, programming interfaces, and a supportive development environment to learn FPGA design. The board is ideal for those looking to dive into the world of hardware design and embedded systems.

![1](./8.png)

[[FPGA Tutorial] Seven-Segment LED Display on Basys 3 FPGA](https://www.fpga4student.com/2017/09/seven-segment-led-display-controller-basys3-fpga.html)

Circuit representation of the Basys 3 Artix-7 Board.

![1](./9.png)

Deeper representation of an individual digit in a four-digit seven segment display. Don’t forget that the challenge in hand is about 5 digits.

![1](./10.png)

💡 To illuminate a segment, the anode should be driven high while the cathode is driven low. However, since the Basys 3 uses transistors to drive enough current into the common anode point, the anode enables are inverted. Therefore, both the AN0..4 and the CA..G/DP signals are driven low when active.

[How to Control 7-Segment Displays on Basys3 FPGA using Verilog in Vivado](https://youtu.be/ORhWNj8li4E?si=GT-nq_l9Uf17SPL3)

![1](./11.png)

Here is a simple example where it gives us a matrix to represent numbers from 0 to 9, since the invertion occurs, the 0s represent which segments are turned on, and 1s when the segments are turned off. Similar to our `fpga_input.xlsx`.

If you’re feeling like binging. Check these out.

[Visualizing Data with 7-Segment Displays](https://youtu.be/hEDQpqhY2MA?si=b87pztqVlgwvn3y8)

[What's The Longest Word You Can Write With Seven-Segment Displays?](https://www.youtube.com/watch?v=zp4BMR88260)

`display.txt`

```bash
└─$ cat display.txt
module display (i,o,anode);
input [4:0]  i;
output reg [6:0]  o;
output [3:0] anode;
assign anode = 4'b0001;

always @(i)
case (i)
    5'b00000 :  o = 7'b1000000;
    5'b00001 :  o = 7'b1111001;
    5'b00010 :  o = 7'b0100100;
    5'b00011 :  o = 7'b0110000;
    5'b00100 :  o = 7'b0011001;
    5'b00101 :  o = 7'b0010010;
    5'b00110 :  o = 7'b0000010;
    5'b00111 :  o = 7'b1111000;
    5'b01000 :  o = 7'b0000000;
    5'b01001 :  o = 7'b0010000;
    5'b01010 :  o = 7'b0001000;
    5'b01011 :  o = 7'b0000011;
    5'b01100 :  o = 7'b1000110;
    5'b01101 :  o = 7'b0100001;
    5'b01110 :  o = 7'b0000100;
    5'b01111 :  o = 7'b0001110;
    5'b10000 :  o = 7'b0001001;
    5'b10001 :  o = 7'b1101111;
    5'b10010 :  o = 7'b1100001;
    5'b10011 :  o = 7'b1000111;
    5'b10100 :  o = 7'b0101011;
    5'b10101 :  o = 7'b0001100;
    5'b10110 :  o = 7'b0011000;
    5'b10111 :  o = 7'b0101111;
    5'b11000 :  o = 7'b0000111;
    5'b11001 :  o = 7'b1000001;
    5'b11010 :  o = 7'b0010001;
    5'b11011 :  o = 7'b1000110;
    5'b11100 :  o = 7'b1110000;
    5'b11101 :  o = 7'b0111111;

    default:  o = 7'b1110111;
endcase

endmodule

// i[0] -> V17
// i[1] -> W16
// i[2] -> W13
// i[3] -> A3
// i[4] -> W2
// anode -> anode display pin
```

`fpga_inputs.xlsx`

![12](./12.png)

```bash
// i[0] -> V17
// i[1] -> W16
// i[2] -> W13
// i[3] -> A3
// i[4] -> W2
```

Now, it’s pretty much a finished job, just get the necessary cells, merge them and reverse them cause of similar MSB concept.

![13](./13.png)

Once you get the individual data, load them into the 7-segment decoder from `dCode`. Which gives you the flag, lot of suspense to a quick finish.

![14](./14.png)

**Flag**: `nite{tr0UbLe_bUbbLe_L0L}`

## Web Exploitation

### **Cybernotes**

I created the world's most secure notes app, but might have uploaded and forgotten about some personal files. Whatever, even if they try to look they will go in the wrong place.

`Author: 1hacker`

[Link](https://cyber-notes.chalz.nitectf2024.live/)

When you visit the page, while digging around you find that the background image is referenced from `/uploads`. [`/uploads/bg.jpg`]

![15](./15.png)

Visiting `/uploads`, we notice couple of interesting logs, seemingly from the future LOL and a Dockerfile.

```bash
└─$ ls
2048-07-21.log  2048-07-24.log  2048-07-26.log  2048-07-28.log
2048-07-23.log  2048-07-25.log  2048-07-27.log  Dockerfile
```

```bash
└─$ cat 2048-07-21.log
Chat Log - Date: 2048-07-21 | Time: 23:47

[Channel: #admin-support]

[23:47]
ShadowGhost: Hey, Admin, you there?

[23:48]
0xA5min: Yes, this is 0xA5min. How can I assist you?

[23:49]
ShadowGhost: I need you to reset my account password. Username: D3aDs0ck.
```

Username acquired. `D3aDs0ck` , and in the same file we have the password mentioned, `bluM#_M@y_N3vr`. Time to login.

![16](./16.png)

Once we login, we see a sort of generic note logging application, before we start anything, let’s finish up with the Dockerfile.

![17](./17.png)

```bash
# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=main.py
ENV JWT_SECRET_KEY=H6jga21h1
ENV FDRP_JWT_SECRET_KEY=wEdAeLdjae

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
```

Here, we see the JWT secret key has been leaked. `H6jga21h1`. Heading over to 

[JWT.IO](https://jwt.io/)

Now, pop out Burp and try logging in again.

![17](./18.png)

For some reason the token didn’t show up on inspecting from the browser. Anyways we got the JWT token. Use the secret key to manipulate the JWT token and send it back to server to get the flag.

```bash
Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZ0FBQUFBQm5ZX2NaUE9jT0JCUkgySXR6SFlvUVFwUWJLNF83aUhuV0ltcEZwWmpQSWl3dmoyZzBmMWVzRGdMZzhIeEdMTGJMQ0N3WGdpSFZ2QkJLTTRUM2w1QmVldzhrd3c9PSIsImV4cCI6MTczNDYwNjAwMH0.3zxLYfbO2wkBy1uFQHlRhu8VyoTdrtygiT6f6xu-K8A
```

![19](./19.png)

If you’re confused on how to do this, just reload the logged in page while proxy is turned on, then send the request to repeater, where you’ll see the original token, change it to the one we got, then send it.

Flag: `nite{7rY_XKcD_S3b_f0R_3xPl4nA7i0n}` 

### **Charlie Hunt 1**

**Flag**: `nite{3rror5_can_b3_u53ful_s0m3t1m35}`

**Author(s)**: `_lunaniverse`

**Description**: Charlie secured his website after an attack on his website. Do you think you can find something?

![20](./20.png)

Visiting the website, we see the option actionable thing to do is to leave a request, so we do the same and capture the request in Burp.

![21](./21.png)

Funny thing is that, it also accepts negative stars HAHA, or pretty much anything we input.

![22](./22.png)

Everything is fine, until you notice the versions in the endpoint. That way we find the very interesting `/v1` endpoint.

💡 APIs (Application Programming Interfaces) often use versioning to differentiate between different versions of the API. This allows the application to introduce new features or changes without breaking backward compatibility with older clients that rely on previous versions of the API.

**Older Versions May Have Known Vulnerabilities**: If the `/v1` endpoint points to an older version of the API, it might contain **known vulnerabilities** that were patched in later versions. Attackers often target these older versions.
**Access Control Issues**: The `/v1` endpoint might expose sensitive data if proper access control isn’t enforced. By inspecting and interacting with the `/v1` API, you could discover weak or misconfigured access control policies.

This way we pull out on interesting error message from the server, with focus on the unknown `__v` variable.

![23](./23.png)

Let’s try exploiting this variable for potential injection through it.

![24](./24.png)

That worked, the server successfully evaluated the expression `1+1` and return `2` under the `__v` variable.

If you’re curious about the use of curly braces here, 

💡 In many web applications, especially those using template engines like **Jinja2** (commonly used with Flask in Python), curly braces are used to **evaluate expressions** and **render dynamic content**. Template engines allow dynamic content to be injected into HTML or JSON responses by evaluating expressions within these curly braces.
Using `Hacktricks` as a resource, 

[HackTricks/jinja2-ssti.md](https://github.com/HackTricks-wiki/hacktricks/blob/master/pentesting-web/ssti-server-side-template-injection/jinja2-ssti.md)

We try out the first payload, `config`, [Add curly braces!] In these object you can find all the configured env variables and dump them.

```bash
HTTP/2 200 OK
Content-Type: application/json
Date: Thu, 19 Dec 2024 11:19:13 GMT
Server: gunicorn
Content-Length: 219

{"error":"Invalid input! The following characters are not allowed: 
config, globals, read, |join, getitem, import, popen, lipsum, request, os, 
subclasses, cat, base, builtins, init, cycler, joiner, namespace, shell, ."}
```

Well that worked. Further,

```bash
Payload = url_for['__gl'+'obals__']['__buil'+'tins__']['op'+'en']('app\\x2epy')['re'+'ad']()
```

Add the curly braces to wrap them payload, for some reason Jekyll disregards them. 

![25](./25.png)

The intent of the payload is to access the python’s global namespace, reach for the built-in functions, use the open() to read the server code (`app.py`).

As for syntax, here’s the explanation.

- `url_for` references a common template function
- Uses string concatenation to bypass potential filters (e.g. `'__gl'+'obals__'`)
- Accesses Python's built-in functions through `__globals__` and `__builtins__`
- Uses hex encoding (`\x2e`) to encode the dot in 'app.py'

Props to [Sibivasan](https://sibivasan.gitbook.io/sibivasan/writeups/2024/nitectf-2024) for the payload.

Flag: `nite{3rror5_can_b3_u53ful_s0m3t1m35}`

![Continue](./continue.jpg)
