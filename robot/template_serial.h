#ifndef __TEMPLATE_SERIAL_H__
#define __TEMPLATE_SERIAL_H__

#include "mbed.h"


class TemplateSerial : public Serial {
public:
    TemplateSerial(PinName tx, PinName rx) : Serial(tx, rx) {}

    void wait_for_stx(){
        uint8_t last = 0x00;

        while(true){
            uint8_t current = getc();
            if(last == 0x10 && current == 0x02){
                break;
            }else{
                last = current;
            }
        }
    }

    template<typename T> T read(){
        uint8_t result[sizeof(T)];

        do{
            wait_for_stx();
            
            for(int i=0; i<sizeof(T); i++){
                result[i] = (uint8_t)getc();
                
                if(i > 0 && result[i - 1] == 0x10){
                    if(result[i] == 0x10){
                        i--;
                    }else{
                        return read<T>();
                    }
                }
            }
        }while(getc() != 0x10 || getc() != 0x03);

        return *((T*)&result);
    }

    template<typename T> void write(T data){
        putc(0x10);
        putc(0x02);

        for(int i=0; i<sizeof(T); i++){
            uint8_t d = ((uint8_t*)&data)[i];

            putc(d);

            if(d == 0x10){
                putc(0x10);
            }
        }

        putc(0x10);
        putc(0x03);
    }
};


#endif