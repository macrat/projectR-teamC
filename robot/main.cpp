#include <limits.h>
#include <stdint.h>

#include "mbed.h"

#include "template_serial.h"
#include "hardware.h"


#pragma pack(1)
struct {
    struct {
        int8_t left, right;
    } body;
    struct {
        int8_t horizontal, vertical, grab;
    } arm;
} typedef control_packet_t;
#pragma pack()


struct {
    struct {
        float left, right;
    } body;
    struct {
        float horizontal, vertical;
        uint8_t grab;
    } arm;
} typedef control_t;


float fixed2float(int8_t bin) {
    return bin / 127.0;
}


control_t parsePacket(control_packet_t packet) {
    return {
        { fixed2float(packet.body.left), fixed2float(packet.body.right) },
        { fixed2float(packet.arm.horizontal), fixed2float(packet.arm.vertical), packet.arm.grab },
    };
}


class Arm {
private:
    static const float hand_opened = 0.75;
    static const float hand_closed = 0.45;
    
    DualMotor arm;
    Servo hand;
    float hand_target;
    
public:
    Arm() : arm(PTC9, PTC8, PTA5, PTA2, PTA12, PTD4, PTA4),
            hand(PTA1) {
        hand = hand_target = hand_opened;
    }
            
    void on_tick() {
        hand = hand + (hand_target - hand)/4.0;
    }
    
    void update(const control_t& packet) {
        arm.setA(packet.arm.horizontal);
        arm.setB(packet.arm.vertical);
        hand_target = packet.arm.grab ? hand_closed : hand_opened;
    }
};


class Body {
private:
    TemplateSerial& serial;
    DualMotor motor;
    
public:
    Body(TemplateSerial& serial) : serial(serial),
        motor(PTE21, PTB1, PTB0, PTE29, PTB3, PTC2, PTB2) {}
    
    void on_tick() {
    }
    
    void update(const control_t& packet) {
        motor.setA(packet.body.right);
        motor.setB(packet.body.left);
    }
};


class TeamC {
private:
    Arm arm;
    Body body;
    Ticker ticker;
    
public:
    TeamC(TemplateSerial& serial) : body(serial) {}
    
    void on_tick() {
        arm.on_tick();
        body.on_tick();
    }
    
    void start() {
        ticker.attach(this, &TeamC::on_tick, 0.1);
    }
    
    void stop() {
        ticker.detach();
    }
    
    void update(const control_t packet) {
        arm.update(packet);
        body.update(packet);
    }
};


int main() {
    TemplateSerial blu(PTE22, PTE23);
    TeamC robot(blu);

    blu.baud(115200);
    
    robot.start();

    while(true){
        robot.update(parsePacket(blu.read<control_packet_t>()));
    }
}
