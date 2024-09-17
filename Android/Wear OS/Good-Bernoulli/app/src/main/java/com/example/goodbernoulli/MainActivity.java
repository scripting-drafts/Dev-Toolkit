package com.example.goodbernoulli;

import static android.widget.Toast.LENGTH_SHORT;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.example.goodbernoulli.databinding.ActivityMainBinding;

import java.util.Arrays;
import java.util.Date;
import java.util.List;
import java.util.Random;

public class MainActivity extends Activity {

    public List<String> sidesList = Arrays.asList("Heads", "Tails");
    public Random rand = new Random();
    public int clicks;
    public long startTime;
    public long elapsedTime;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        com.example.goodbernoulli.databinding.ActivityMainBinding binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());
    }

    public void flipCoin(View view){
        clicksCheck();
        TextView coinText = findViewById(R.id.text);
        String coinSide = sidesList.get(rand.nextInt(sidesList.size()));
        coinText.setText(coinSide);
        clicksTimer();
    }

    public void clicksCheck(){
        if (clicks == 3){ clicks = 0; }
        clicks += 1;
    }

    public void clicksTimer(){
        if (clicks == 1){
            startTime = System.currentTimeMillis();
        }
        else if (clicks == 3){
            elapsedTime = (new Date()).getTime();
            if (elapsedTime - startTime < 1000){
                Toast.makeText(this, "Chill man!", LENGTH_SHORT).show(); // coinText.setText("Chill man.");
            }
        }
    }
}