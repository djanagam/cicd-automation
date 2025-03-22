pipeline {
    agent any

    stages {
        stage('Checkout Source Code') {
            steps {
                git branch: 'main', url: 'git@github.com:your-repo/xml-files.git'
            }
        }

        stage('Parse XML Files Using SAX') {
            steps {
                script {
                    def javaCode = '''
                    import java.io.File;
                    import java.io.FileInputStream;
                    import javax.xml.parsers.SAXParser;
                    import javax.xml.parsers.SAXParserFactory;
                    import org.xml.sax.Attributes;
                    import org.xml.sax.SAXException;
                    import org.xml.sax.helpers.DefaultHandler;

                    public class SAXXMLParser {
                        public static void main(String[] args) {
                            String[] xmlFiles = { "file1.xml", "file2.xml", "file3.xml" }; // List of files to parse

                            for (String fileName : xmlFiles) {
                                File file = new File(fileName);
                                if (!file.exists()) {
                                    System.err.println("File not found: " + fileName);
                                    continue;
                                }

                                System.out.println("Parsing: " + fileName);
                                try {
                                    SAXParserFactory factory = SAXParserFactory.newInstance();
                                    SAXParser saxParser = factory.newSAXParser();
                                    DefaultHandler handler = new DefaultHandler() {
                                        public void startElement(String uri, String localName, String qName, Attributes attributes) {
                                            System.out.println("Start Element: " + qName);
                                        }
                                    };
                                    saxParser.parse(new FileInputStream(file), handler);
                                    System.out.println("Successfully parsed: " + fileName);
                                } catch (SAXException e) {
                                    System.err.println("SAX Parsing error in file: " + fileName);
                                    System.err.println("Error: " + e.getMessage());
                                } catch (Exception e) {
                                    System.err.println("Unexpected error in file: " + fileName);
                                    e.printStackTrace();
                                }
                            }
                        }
                    }
                    ''';

                    writeFile file: 'SAXXMLParser.java', text: javaCode
                    sh 'javac SAXXMLParser.java'
                    sh 'java SAXXMLParser'
                }
            }
        }
    }
}