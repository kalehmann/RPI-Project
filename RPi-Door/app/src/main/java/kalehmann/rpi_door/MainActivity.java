package kalehmann.rpi_door;

import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.preference.PreferenceManager;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.Switch;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;

public class MainActivity extends AppCompatActivity implements CompoundButton.OnCheckedChangeListener {

    private SharedPreferences sharedPrefs;
    private Switch mSwitch;
    private EditText urlText;

    private class DoorChangerTask extends AsyncTask<String, Integer, Boolean> {

        private URL myUrl;
        private int responseCode = 0;
        private Switch mySwitch;

        public DoorChangerTask(Switch mySwitch) {
            super();
            this.mySwitch = mySwitch;
        }

        protected Boolean doInBackground(String... uri) {
            try {
                myUrl = new URL(uri[0]);
                Log.w("Hi", uri[0]);
                responseCode = ((HttpURLConnection) myUrl.openConnection()).getResponseCode();
            } catch (MalformedURLException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }

            if (responseCode == 200) {
                return true;
            } else {
                return false;
            }
        }
    }

    @Override
    public void onCheckedChanged(CompoundButton compoundButton, boolean checked) {

        String uri = urlText.getText().toString();
        SharedPreferences.Editor editor = sharedPrefs.edit();
        editor.putString("kalehmann.rpi_door.door_uri", uri);
        editor.commit();

        if (!uri.startsWith("http://")) {
            uri = "http://" + uri;
        }
        if (!uri.endsWith("/")) {
            uri = uri + ":6000/";
        } else {
            uri = uri.substring(0, uri.length()-1) + ":6000/";
        }
        if (checked) {
            uri = uri + "open_door";
            compoundButton.setText("Open");
        } else {
            uri = uri + "close_door";
            compoundButton.setText("Closed");
        }
        new DoorChangerTask(mSwitch).execute(uri);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mSwitch = (Switch) findViewById(R.id.myswitch);
        mSwitch.setOnCheckedChangeListener(this);

        urlText = (EditText) findViewById(R.id.url);

        sharedPrefs = PreferenceManager.getDefaultSharedPreferences(this);
        urlText.setText(sharedPrefs.getString("kalehmann.rpi_door.door_uri", ""));
    }
}
