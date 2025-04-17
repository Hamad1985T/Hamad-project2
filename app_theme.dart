import 'package:flutter/material.dart';

class AppTheme {
  static final ThemeData lightTheme = ThemeData(
    primarySwatch: Colors.blue,
    fontFamily: 'DroidKufi',
    textTheme: TextTheme(
      headline1: TextStyle(fontSize: 24.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      headline2: TextStyle(fontSize: 22.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      headline3: TextStyle(fontSize: 20.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      headline4: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      headline5: TextStyle(fontSize: 16.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      headline6: TextStyle(fontSize: 14.0, fontWeight: FontWeight.bold, fontFamily: 'DroidKufi'),
      bodyText1: TextStyle(fontSize: 16.0, fontFamily: 'DroidKufi'),
      bodyText2: TextStyle(fontSize: 14.0, fontFamily: 'DroidKufi'),
    ),
    appBarTheme: AppBarTheme(
      centerTitle: true,
      titleTextStyle: TextStyle(
        fontFamily: 'DroidKufi',
        fontSize: 20.0,
        fontWeight: FontWeight.bold,
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        textStyle: TextStyle(
          fontFamily: 'DroidKufi',
          fontSize: 16.0,
        ),
        padding: EdgeInsets.symmetric(vertical: 12.0, horizontal: 24.0),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(),
      labelStyle: TextStyle(
        fontFamily: 'DroidKufi',
        fontSize: 16.0,
      ),
      contentPadding: EdgeInsets.symmetric(vertical: 16.0, horizontal: 16.0),
    ),
  );
}
