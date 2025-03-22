pipeline {
    agent any

    stages {
        stage('Create XML File') {
            steps {
                script {
                    def xmlContent = """<?xml version="1.0" encoding="UTF-8"?>
                    <root>
                        <message>Hello, Jenkins!</message>
                    </root>
                    """
                    writeFile file: 'sample.xml', text: xmlContent
                }
            }
        }

        stage('Parse XML with Java') {
            steps {
                script {
                    def javaCode = '''
                    import java.io.File;
                    import javax.xml.parsers.DocumentBuilder;
                    import javax.xml.parsers.DocumentBuilderFactory;
                    import org.w3c.dom.Document;
                    import org.xml.sax.SAXParseException;

                    public class XMLParser {
                        public static void main(String[] args) {
                            try {
                                File xmlFile = new File("sample.xml");
                                DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
                                DocumentBuilder builder = factory.newDocumentBuilder();
                                Document doc = builder.parse(xmlFile);
                                doc.getDocumentElement().normalize();
                                System.out.println("Root Element: " + doc.getDocumentElement().getNodeName());
                            } catch (SAXParseException e) {
                                System.err.println("Parsing error at line " + e.getLineNumber() + ", column " + e.getColumnNumber());
                                e.printStackTrace();
                            } catch (Exception e) {
                                e.printStackTrace();
                            }
                        }
                    }
                    '''
                    writeFile file: 'XMLParser.java', text: javaCode
                    sh 'javac XMLParser.java'
                    sh 'java XMLParser'
                }
            }
        }
    }
}