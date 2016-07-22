#ifndef __HARDWARE_H__
#define __HARDWARE_H__

#include "mbed.h"
#include "TB6612FNG.h"


// Futaba RS304MD control class
class Servo {
private:
    const static float min =  560 / 1000.0 / 1000.0;
    const static float max = 2480 / 1000.0 / 1000.0;
    const static float range = max - min;
    const static float period = 20;
    
    PwmOut sig;
    float value;

public:
    Servo(PinName pin) : sig(pin) {
        sig.period_ms(period);
    }
    
    Servo& operator =(float val) {
        value = val;
        sig.pulsewidth(min + range * val);
        return *this;
    }
    
    operator float() const {
        return value;
    }
};


// Toshiba TB6612FNG control class
class DualMotor {
private:
    const static float period = 1.0 / 50.0 / 1000.0;  // 50KHz
    
    TB6612FNG controller;
    float a_value, b_value;
    
public:
    DualMotor(PinName pwm_a, PinName a_in1, PinName a_in2, PinName pwm_b, PinName b_in1, PinName b_in2, PinName stby)
            : controller(pwm_a, a_in1, a_in2, pwm_b, b_in1, b_in2, stby) {
        controller.motorA_stop();
        controller.motorB_stop();
        a_value = b_value = 0.0;
    }
    
    void setA(float val) {
        a_value = val;
        
        if(val == 0.0){
            controller.motorA_stop();
        }else if(val > 0.0){
            controller.setPwmApulsewidth(val);
            controller.motorA_cw();
        }else{
            controller.setPwmApulsewidth(-val);
            controller.motorA_ccw();
        }
    }
    
    void setB(float val) {
        b_value = val;
        
        if(val == 0.0){
            controller.motorB_stop();
        }else if(val > 0.0){
            controller.setPwmBpulsewidth(val);
            controller.motorB_cw();
        }else{
            controller.setPwmBpulsewidth(-val);
            controller.motorB_ccw();
        }
    }
    
    float getA() const {
        return a_value;
    }
    
    float getB() const {
        return b_value;
    }
};


// Single channel motor driver control class
class SingleMotor {
private:
    const static float period = 1.0 / 1000.0;
    
    PwmOut a, b;
    
public:
    SingleMotor(PinName a, PinName b) : a(a), b(b) {
        this->a.period(period);
        this->b.period(period);
    }
    
    void set(float val) {
        if(val == 0.0){
            a = b = 0.0;
        }else if(val > 0.0){
            a = 1.0 - val;
            b = 1.0;
        }else{
            a = 1.0;
            b = 1.0 + val;
        }
    }
    
    SingleMotor& operator =(float val) {
        set(val);
        return *this;
    }
};


// onboard LED controller
class Led {
public:
    PwmOut red, green, blue;
    
    Led() : red(LED_RED), green(LED_GREEN), blue(LED_BLUE) {
        red = green = blue = 1.0;
    }
};


// reflection photon sensor controller
class ReflectionPhoton {
private:
    const static float weight = 0.9;

    DigitalOut light;
    AnalogIn sensor;
    Ticker ticker;
    float value;

public:
    ReflectionPhoton(PinName light, PinName sensor) : light(light), sensor(sensor) {}

    void scan() {
        light = 0;
        float on(sensor);

        wait(0.01);

        light = 1;
        float newval = (on - sensor);

        value = value*weight + (1.0 - weight)*newval;
    }

    void start() {
        ticker.attach(this, &ReflectionPhoton::scan, 0.05);
    }

    void stop() {
        ticker.detach();
    }

    float get() const {
        return value;
    }

    operator float() const {
        return get();
    }
};


// PSD distance sensor controller
class PSDSensor {
private:
    const static float weight = 0.9;
    
    AnalogIn sensor;
    float value;
    
public:
    PSDSensor(PinName in) : sensor(in) {
        value = sensor;
    }
    
    void scan() {
        value = value*weight + sensor*(1.0-value);
    }
    
    float get() const {
        return value;
    }
    
    operator float() const {
        return get();
    }
};


#endif