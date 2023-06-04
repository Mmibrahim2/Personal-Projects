// Created by Mohammud Ibrahim

import com.twilio.Twilio;
import com.twilio.rest.api.v2010.account.Message;
import com.twilio.type.PhoneNumber;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.URLConnection;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class WeatherText {
    public static final String ACCOUNT_SID = "REMOVED";
    public static final String AUTH_TOKEN = "REMOVED";
    public static final String API_KEY = "REMOVED";
    public static final String TO_PHONE_NUMBER = "REMOVED";
    public static final String LOCATION = "Madison";
    public static final int HOUR_OF_DAY = 6;
    public static final int MINUTE = 30;

    public static void main(String[] args) {
        // Initialize the Twilio client
        Twilio.init(ACCOUNT_SID, AUTH_TOKEN);
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(() -> sendTextMessage(), 0, 1, TimeUnit.DAYS);
    }

    public static void sendTextMessage() {
        try {
            // Build the OpenWeatherMap API URL
            String apiUrl = "https://api.openweathermap.org/data/2.5/weather?q=" + LOCATION + "&appid=" + API_KEY;
            URL url = new URL(apiUrl);
            URLConnection conn = url.openConnection();
            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            StringBuilder response = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                response.append(line);
            }
            JSONObject json = new JSONObject(response.toString());
            JSONObject main = json.getJSONObject("main");
            double temperature = main.getDouble("temp");
            JSONObject weather = json.getJSONArray("weather").getJSONObject(0);
            String description = weather.getString("description");
            StringBuilder message = new StringBuilder();
            message.append("Good morning! The weather today is ");
            message.append(description.toLowerCase());
            message.append(". ");
            if (temperature < 10) {
                message.append("It's cold outside, so make sure to wear warm clothes and a jacket.");
            } else if (temperature < 20) {
                message.append("It's a bit chilly, so you might want to wear a sweater or a light jacket.");
            }
            Message sms = Message.creator(new PhoneNumber(TO_PHONE_NUMBER),
                    new PhoneNumber("TWILIO_PHONE_NUMBER"),
                    message.toString()).create();
            System.out.println("Text message sent to " + TO_PHONE_NUMBER);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }
}
