package br.botossi.photoscraper.services;

import java.util.List;

public interface PhotoScraperService {
    void downloadPhotos(String url);

    void getPhotos(String hotelName);

    List<String> getDownloadedProperties();
}
