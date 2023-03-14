// Test Code for MCP3208s ADCs 12bit 8 Channel (SPI)
#include <SPI.h>
#include <Wire.h>
#include <errno.h>
#include <MIDI.h>
#include <serialMIDI.h>
#include <SoftwareSerial.h>

#define IO_EXP_RESET_PIN (A0) //Active Low
#define IO_EXP_INT0_PIN (2)
#define IO_EXP_INT1_PIN (3)
#define IO_EXP_I2C_ADDR (B0100000)

#define ADC_CHIP_SELECT_1_PIN (10) //Active Low
#define ADC_CHIP_SELECT_2_PIN (A3) //Active Low
#define ADC_SPI_MOSI_PIN (11)
#define ADC_SPI_MISO_PIN (12)
#define ADC_SPI_SCK_PIN (13)

#define YELLOW_LED_PIN (7)
#define RED_LED_PIN (8)
#define GREEN_LED_PIN (9)

#define MIDI_TX (A2) // PCB v1 requires rework for this.
#define MIDI_RX (A1)

#define SWITCH_OUT_PIN (6)

void setup()
{
    pinMode(SWITCH_OUT_PIN, OUTPUT);
    digitalWrite(SWITCH_OUT_PIN, LOW);

    setup_LEDs();
    //VC ADC IO Setup MCP3208s
    setupADCs();
    setup_io_expander();

    Serial.begin(115200);

    setup_midi();
    delay(100);
}

void loop()
{
    loop_serial_read();
    loop_led_update();
    loop_test_adc();
    loop_io_expander();
    //loop_midi();
}

using Transport = MIDI_NAMESPACE::SerialMIDI<SoftwareSerial>;
SoftwareSerial mySerial = SoftwareSerial(MIDI_RX, MIDI_TX);
Transport serialMIDI(mySerial);
MIDI_NAMESPACE::MidiInterface<Transport> MIDI((Transport &)serialMIDI);
static uint8_t midi_channel = 11;
void setup_midi()
{
    MIDI.begin(midi_channel);
}

static unsigned long last_midi_update = millis();
static uint8_t toggle = true;
void loop_midi(void)
{
    if (time_check_and_update(&last_midi_update, 250))
    {
        if (toggle)
        {
            MIDI.sendNoteOn(45, 127, midi_channel);
        }
        else
        {
            MIDI.sendNoteOff(45, 0, midi_channel);
        }
        toggle = !toggle;
    }
}

static unsigned long last_serial_update = millis();
static char input_buff[100];
static uint8_t input_buff_idx = 0;
boolean my_read_analog = false;
boolean my_read_digital = false;
boolean my_write_digital = false;
static unsigned int my_write_io_value = 0;

void loop_serial_read(void)
{
    if (time_check_and_update(&last_serial_update, 50))
    {
        char c = Serial.read();
        while (c >= 0)
        {
            if (c == '\0' || c == '\n' || c == '\r')
            {
                c = '\n';
            }
            if (input_buff_idx < sizeof(input_buff))
            {
                input_buff[input_buff_idx] = c;
                input_buff_idx++;
                if (c != '\n')
                {
                    Serial.print(c); //echos
                    c = Serial.read();
                }
                else
                {
                    Serial.println();
                    c = -1;
                }
            }
        }
        if (input_buff_idx > 0 && input_buff[input_buff_idx - 1] == '\n')
        {
            input_buff[input_buff_idx] = '\0';
            handle_command(input_buff, ++input_buff_idx);
            memset(input_buff, 0, input_buff_idx);
            input_buff_idx = 0;
        }
    }
}

static boolean command_match(char const *const buf, uint8_t size, char const *const command)
{
    return 0 == strncmp(buf, command, min(size, strlen(command)));
}

void handle_command(char const *const buf, uint8_t size)
{
    if (command_match(buf, size, "read_analog"))
    {
        my_read_analog = true;
    }
    else if (command_match(buf, size, "read_digital"))
    {
        my_read_digital = true;
    }
    else if (command_match(buf, size, "write_digital="))
    {
        my_write_io_value = strtoul(&buf[14], NULL, 16);
        if (errno > 0)
        {
            Serial.print("error=");
            Serial.println(errno);
            errno = 0;
        }
        else
        {
            // Serial.print(my_write_io_value);
            // printBufHEX(my_write_io_value);
            // Serial.println();
            my_write_digital = true;
        }
    }
    else if (command_match(buf, size, "midi_note_on="))
    {
        uint8_t note = strtoul(&buf[13], NULL, 10);
        if (errno > 0)
        {
            Serial.print("error=");
            Serial.println(errno);
            errno = 0;
        }
        else
        {
            MIDI.sendNoteOn(note, 127, midi_channel);
            Serial.println("sent");
        }
    }
    else if (command_match(buf, size, "midi_note_off="))
    {
        uint8_t note = strtoul(&buf[14], NULL, 10);
        if (errno > 0)
        {
            Serial.print("error=");
            Serial.println(errno);
            errno = 0;
        }
        else
        {
            MIDI.sendNoteOff(note, 0, midi_channel);
            Serial.println("sent");
        }
    }
    else if (command_match(buf, size, "midi_change_mode="))
    {
        uint8_t mode = strtoul(&buf[17], NULL, 10);
        if (errno > 0)
        {
            Serial.print("error=");
            Serial.println(errno);
            errno = 0;
        }
        else
        {
            // DataEntryLSB (38) is used in the DUT to allow mode changes.
            MIDI.sendControlChange(midi::MidiControlChangeNumber::DataEntryLSB, mode, midi_channel);
            Serial.println("sent");
        }
    }
    else if (command_match(buf, size, "midi_all_sound_off"))
    {
        MIDI.sendControlChange(midi::MidiControlChangeNumber::AllSoundOff, 0, midi_channel);
        Serial.println("sent");
    }
    else if (command_match(buf, size, "midi_all_notes_off"))
    {
        MIDI.sendControlChange(midi::MidiControlChangeNumber::AllNotesOff, 0, midi_channel);
        Serial.println("sent");
    }
    else if (command_match(buf, size, "switch_on"))
    {
        digitalWrite(SWITCH_OUT_PIN, HIGH);
        Serial.println("on");
    }
    else if (command_match(buf, size, "switch_off"))
    {
        digitalWrite(SWITCH_OUT_PIN, LOW);
        Serial.println("off");
    }
    else
    {
        Serial.println("bad_command");
    }
}

enum
{
    LED_OFF,
    BLINK_ON,
    BLINK_OFF,
    BLINK_FAST_ON,
    BLINK_FAST_OFF,
    SOLID_ON,
    LED_STATE_CNT,
};
typedef unsigned char led_state_type;

typedef struct
{
    uint8_t pin;
    led_state_type state;
    unsigned long last_change;
} led_type;

static led_type leds[] = {
    {RED_LED_PIN, SOLID_ON, millis()},
    {GREEN_LED_PIN, BLINK_ON, millis()},
    {YELLOW_LED_PIN, BLINK_FAST_ON, millis()},
};

void setup_LEDs(void)
{
    pinMode(RED_LED_PIN, OUTPUT);
    pinMode(GREEN_LED_PIN, OUTPUT);
    pinMode(YELLOW_LED_PIN, OUTPUT);
}

static unsigned long last_led_update = millis();
void loop_led_update(void)
{
    if (time_check_and_update(&last_led_update, 50))
    {
        for (uint8_t i = 0; i < sizeof(leds) / sizeof(leds[0]); i++)
        {
            switch (leds[i].state)
            {
            case BLINK_ON:
                if (time_check_and_update(&(leds[i].last_change), 500))
                {
                    digitalWrite(leds[i].pin, LOW);
                    leds[i].state = BLINK_OFF;
                }
                break;
            case BLINK_OFF:
                if (time_check_and_update(&(leds[i].last_change), 500))
                {
                    digitalWrite(leds[i].pin, HIGH);
                    leds[i].state = BLINK_ON;
                }
                break;
            case BLINK_FAST_ON:
                if (time_check_and_update(&(leds[i].last_change), 250))
                {
                    digitalWrite(leds[i].pin, LOW);
                    leds[i].state = BLINK_FAST_OFF;
                }
                break;
            case BLINK_FAST_OFF:
                if (time_check_and_update(&(leds[i].last_change), 500))
                {
                    digitalWrite(leds[i].pin, HIGH);
                    leds[i].state = BLINK_FAST_ON;
                }
                break;
            case SOLID_ON:
                digitalWrite(leds[i].pin, HIGH);
                leds[i].last_change = last_led_update;
                break;
            case LED_OFF:
            default:
                digitalWrite(leds[i].pin, LOW);
                leds[i].last_change = last_led_update;
                break;
            }

            // Serial.print("led_state=");
            // Serial.println(leds[i].state);
        }
    }
}

/**
 * Setup IO pins for the MCP3208s ADCs.
 */
void setupADCs()
{
    //VC DAC IO Setup MCP4922
    pinMode(ADC_CHIP_SELECT_1_PIN, OUTPUT);
    digitalWrite(ADC_CHIP_SELECT_1_PIN, HIGH);
    pinMode(ADC_CHIP_SELECT_2_PIN, OUTPUT);
    digitalWrite(ADC_CHIP_SELECT_2_PIN, HIGH);
    SPI.begin();
    //Lower the frequency of the SPI clock, the 4MHz default is out of spec (2MHz max)
    //SPI_MODE1 makes sure the trailing edge is used to sample MISO, this matches the spec and improved the MOSI waveform.
    SPI.beginTransaction(SPISettings(125000, MSBFIRST, SPI_MODE1));
}

/**
 * Read ADC channel
 */
void readADC(uint8_t chip_select_pin, uint8_t channel, unsigned int *const value)
{
    //uint8_t buf[3] = {8, 16, 32};
    uint8_t buf[3] = {6 | (channel >> 2), channel << 6, 0};
    // Serial.print("out=0x");
    // printBufHEX(buf, 3);
    // Serial.println();
    digitalWrite(chip_select_pin, LOW);
    SPI.transfer(buf, 3);
    digitalWrite(chip_select_pin, HIGH);
    // Serial.print(" in=0x");
    // printBufHEX(buf, 3);
    // Serial.println();
    *value = buf[2] | (((uint16_t)buf[1] & 0x0F) << 8);
}

void printBufHEX(unsigned int val16)
{
    char output[5];
    snprintf(output, 5, "%04X", val16);
    Serial.print(output);
}

void printBufHEX(void const *const buf, int cnt)
{
    char output[3];
    for (int i = 0; i < cnt; i++)
    {
        output[0] = 0;
        snprintf(output, 3, "%02X", ((char *)buf)[i]);
        Serial.print(output);
    }
}
static unsigned long last_adc_read = millis();
static unsigned char channel = 0;
#define ANALOG_PINS 16
static unsigned int latest_values[ANALOG_PINS];
void loop_test_adc()
{
    if (time_check_and_update(&last_adc_read, 100) && my_read_analog)
    {
        for (uint8_t i = 0; i < ANALOG_PINS; i++)
        {
            latest_values[i] = 0xFFFF;
            readADC(i < 8 ? ADC_CHIP_SELECT_2_PIN : ADC_CHIP_SELECT_1_PIN, i & 0x7, &latest_values[i]);

            // Serial.print(i);
            // Serial.print("=");
            // Serial.println(atest_values[i], HEX);
        }
        Serial.print("analog_values=");
        for (uint8_t i = 0; i < ANALOG_PINS; i++)
        {
            latest_values[i];
            printBufHEX(latest_values[i]);
            Serial.print(",");
        }
        Serial.println();
        my_read_analog = false;
    }
}

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

static unsigned long last_io_write = millis();
static unsigned int io_value = 1;
void loop_io_expander()
{
    if (time_check_and_update(&last_io_write, 50))
    {
        if (my_read_digital)
        {
            setup_io_expander_as_inputs();
            io_exp_read_pins(&io_value);
            Serial.print("digital_values=");
            printBufHEX(io_value);
            Serial.println();
            my_read_digital = false;
        }
        if (my_write_digital)
        {
            setup_io_expander_as_outputs();
            io_exp_set_pins(my_write_io_value);
            my_write_digital = false;
            Serial.println("write_done");
        }
    }
}

void io_exp_read_pins(unsigned int *value)
{
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(GPIOA);
    Wire.endTransmission(true);
    Wire.requestFrom(IO_EXP_I2C_ADDR, 2);
    byte buff[2];
    Wire.readBytes(buff, 2);
    *value = buff[1];
    *value = *value << 8;
    *value |= buff[0];

    //*value = Wire.read();
    // *value = *value << 8 | Wire.read();
    //Wire.endTransmission(true);
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
    setup_io_expander_as_inputs();
    delay(10);
}

void setup_io_expander_as_inputs()
{
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(IODIRA);
    Wire.write(0xFF);
    Wire.write(0xFF);
    Wire.endTransmission(true);
    //Turn off pullups
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(GPPUA);
    Wire.write(0);
    Wire.write(0);
    Wire.endTransmission(true);
}

void setup_io_expander_as_outputs()
{
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(IODIRA);
    Wire.write(0);
    Wire.write(0);
    Wire.endTransmission(true);
    //Turn on pullups
    Wire.beginTransmission(IO_EXP_I2C_ADDR);
    Wire.write(GPPUA);
    Wire.write(0xFF);
    Wire.write(0xFF);
    Wire.endTransmission(true);
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
