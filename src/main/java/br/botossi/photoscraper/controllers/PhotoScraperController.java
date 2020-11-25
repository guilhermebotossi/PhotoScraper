package br.botossi.photoscraper.controllers;

import br.botossi.photoscraper.services.PhotoScraperService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import javax.websocket.server.PathParam;
import java.util.List;

@RestController
public class PhotoScraperController {

    private PhotoScraperService photoScraperService;

    @Autowired
    public PhotoScraperController(PhotoScraperService photoScraperService){
        this.photoScraperService = photoScraperService;
    }

    @PostMapping(path = "download", consumes = "application/json")
    public void downloadPhotos(@RequestBody String url){
        photoScraperService.downloadPhotos(url);
    }

    @GetMapping(path = "property/list")
    public List<String> getDownloadedProperties() {
        return photoScraperService.getDownloadedProperties();
    }

    @GetMapping(path = "photos/{hotelName}")
    public void getPhotos(@PathParam("hotelName") String hotelName) {
        photoScraperService.getPhotos(hotelName);
    }
}
