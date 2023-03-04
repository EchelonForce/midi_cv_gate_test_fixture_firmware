// Test Code for MCP3208s ADCs 12bit 8 Channel (SPI)
#include <SPI.h>

#define ADC_CHIP_SELECT_PIN (10) //Active Low
#define ADC_SPI_MOSI_PIN (11)
#define ADC_SPI_MISO_PIN (12)
#define ADC_SPI_SCK_PIN (13)
#define LED_PIN (9)

void setup()
{
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    //VC ADC IO Setup MCP3208s
    setupADCs();

    Serial.begin(115200);
    delay(100);
}

void loop()
{
    loop_test_adc();
}

/**
 * Setup IO pins for the MCP3208s ADCs.
 */
void setupADCs()
{
    //VC DAC IO Setup MCP4922
    pinMode(ADC_CHIP_SELECT_PIN, OUTPUT);
    digitalWrite(ADC_CHIP_SELECT_PIN, HIGH);

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
    Serial.print("out=0x");
    printBufHEX(buf, 3);
    Serial.println();
    digitalWrite(chip_select_pin, LOW);
    SPI.transfer(buf, 3);
    digitalWrite(chip_select_pin, HIGH);
    Serial.print(" in=0x");
    printBufHEX(buf, 3);
    Serial.println();
    *value = buf[2] | (((uint16_t)buf[1] & 0x0F) << 8);
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
static unsigned long last_led_update = millis();
static unsigned long last_adc_read = millis();
static unsigned char channel = 0;
void loop_test_adc()
{
    if (time_check_and_update(&last_adc_read, 1000))
    {
        unsigned int latest_value = 0xFFFF;
        readADC(ADC_CHIP_SELECT_PIN, channel, &latest_value);
        Serial.print(channel);
        Serial.print("=");
        Serial.println(latest_value, HEX);
        Serial.print(channel);
        Serial.print("=");
        Serial.println(latest_value);
        Serial.print(channel);
        Serial.print("=");
        Serial.println((float)latest_value / (4095 / 5.155), 3);
        channel += 1;
        channel = channel % 8;
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