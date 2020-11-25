package br.botossi.photoscraper.services;

import kotlin.collections.ArrayDeque;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.apache.tomcat.util.http.fileupload.FileUtils;
import org.jsoup.Jsoup;
import org.jsoup.nodes.DataNode;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.nodes.TextNode;
import org.jsoup.safety.Whitelist;
import org.jsoup.select.Elements;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.*;
import java.net.MalformedURLException;
import java.net.URI;
import java.net.URL;
import java.net.URLDecoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Service
public class DefaultPhotoScraperService implements PhotoScraperService{

    private String propertiesPath = "static/properties/";


    @Override
    public void downloadPhotos(String url) {
        try {

            url = URLDecoder.decode(url, StandardCharsets.UTF_8.name());
            Elements scripts = Jsoup.connect(url).get().getElementsByTag("script");

            String content = null;
            for(Element e : scripts){
                if (e.data().contains("hotelPhotos")) {
                     content  = e.html();
                     break;
                }
            }

            Matcher matcher = Pattern.compile("highres_url: '(https:\\/\\/.*?\\.jpg(?:\\?.*?)?)'").matcher(content);
            List<String> urls = new ArrayList<>();

            while(matcher.find()) {
                urls.add(matcher.group(1));
            }

            String hotelName = getHotelName(url);
            Path destination = Path.of(propertiesPath + hotelName);

            if(Files.notExists(destination)) {
                Files.createDirectory(destination);
            }


            for (String photoUrl : urls) {
                saveImage(photoUrl, destination.toAbsolutePath().toString() + "/" + getFilename(photoUrl));
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }



    @Override
    public void getPhotos(String hotelName) {

    }

    @Override
    public List<String> getDownloadedProperties() {
        return Arrays.stream(Objects.requireNonNull(new File(propertiesPath).listFiles(File::isDirectory))).map(File::getName).collect(Collectors.toList());
    }


    private String getHotelName(String url) throws MalformedURLException {
        String filename = getFilename(url);
        return filename.substring(0 ,filename.lastIndexOf('.'));
    }

    private String getFilename(String url) throws MalformedURLException{
        URL urlObj = new URL(url);
        String urlPath = urlObj.getPath();
        return urlPath.substring(urlPath.lastIndexOf('/') + 1);
    }

    public static void saveImage(String imageUrl, String destinationFile) throws IOException {
        URL url = new URL(imageUrl);
        InputStream is = url.openStream();
        OutputStream os = new FileOutputStream(destinationFile);

        byte[] b = new byte[2048];
        int length;

        while ((length = is.read(b)) != -1) {
            os.write(b, 0, length);
        }

        is.close();
        os.close();
    }
}
