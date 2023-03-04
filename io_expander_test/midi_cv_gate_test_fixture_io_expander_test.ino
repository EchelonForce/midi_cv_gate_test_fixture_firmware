// Test Code for MCP23018s 16 pin I2C IO Expander
#include <Wire.h>

#define IO_EXP_RESET_PIN (A0) //Active Low
#define IO_EXP_INT0_PIN (2)
#define IO_EXP_INT1_PIN (3)
#define LED_PIN (13)
#define IO_EXP_I2C_ADDR (B0100000)

enum mcp23018_registers //Register addresses with BANK set to 0
{
    IODIRA = 0x00,
    IODIRB = 0x01,
    IPOLA = 0x02,
    IPOLB = 0x03,
    GPINTENA = 0x04,
    GPINTENB = 0x05,
    DEFVALA = 0x06,
    DEFVALB = 0x07,
    INTCONA = 0x08,
    INTCONB = 0x09,
    IOCON = 0x0A, //and 0x0B,
    GPPUA = 0x0C,
    GPPUB = 0x0D,
    INTFA = 0x0E,
    INTFB = 0x0F,
    INTCAPA = 0x10,
    INTCAPB = 0x11,
    GPIOA = 0x12,
    GPIOB = 0x13,
    OLATA = 0x14,
    OLATB = 0x15,
};

enum intcon_reg_bits
{
    INTCC = 0x00,
    INTPOL = 0x01,
    ODR = 0x02,
    SEQOP = 0x05,
    MIRROR = 0x06,
    BANK = 0x07,
};

void setup()
{
    setup_io_expander();

    //VC ADC IO Setup MCP3208s
    Serial.begin(115200);
    delay(100);
}

void loop()
{
    loop_io_expander();
}

static unsigned long last_led_update = millis();
static unsigned long last_io_write = millis();
unsigned int io_value = 1;
void loop_io_expander()
{
    if (time_check_and_update(&last_io_write, 50))
    {
        io_exp_set_pins(io_value);
        shift(&io_value);
    }

    if (time_check_and_update(&last_led_update, 2500))
    {
        if (digitalRead(LED_PIN))
        {
            digitalWrite(LED_PIN, LOW);
        }
        else
        {
            digitalWrite(LED_PIN, HIGH);
        }
    }
}

void blink(unsigned int *value)
{
    if (*value == 0 || *value == 0xFFFF)
    {
        *value = ~*value;
    }
    else
    {
        *value = 0;
    }
}

void shift(unsigned int *value)
{
    *value = *value << 1;
    if (*value == 0)
    {
        *value = 1;
    }
}
void io_exp_set_pins(unsigned int value)
{
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(GPIOA);
    Wire.write(value);
    Wire.write(value >> 8);
    Wire.endTransmission(true);
}

void setup_io_expander()
{
    pinMode(IO_EXP_RESET_PIN, OUTPUT);
    digitalWrite(IO_EXP_RESET_PIN, HIGH);
    attachInterrupt(digitalPinToInterrupt(IO_EXP_INT0_PIN), interrupt_0, CHANGE);
    attachInterrupt(digitalPinToInterrupt(IO_EXP_INT1_PIN), interrupt_1, CHANGE);

    Wire.begin(IO_EXP_I2C_ADDR);
    delay(10);

    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(IOCON);
    Wire.write(0);
    Wire.endTransmission(true);
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(IODIRA);
    Wire.write(0);
    Wire.write(0);
    Wire.endTransmission(true);
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(GPPUA);
    Wire.write(0xFF);
    Wire.write(0xFF);
    Wire.endTransmission(true);

    delay(10);
}

void interrupt_0() {}
void interrupt_1() {}

/**
 * Check the passed in time (in milliseconds) agains current time and if delta
 * ms has passed return true and set passed in time to current time.
 */
uint8_t time_check_and_update(unsigned long *prev_update, unsigned long delta)
{
    unsigned long now = millis();
    uint8_t ret = (now - *prev_update) > delta;
    if (ret)
    {
        *prev_update = now;
    }
    return ret;
}
