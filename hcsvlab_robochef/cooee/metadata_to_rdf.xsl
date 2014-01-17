<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
	  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
	  xmlns:dc="http://purl.org/dc/terms/"
	  xmlns:foaf="http://xmlns.com/foaf/0.1/">
	

  <xsl:output method="xml" indent="yes"/>
     
	<xsl:template match="/properties">
		<rdf:RDF>
		  <rdf:Description>
		  	<xsl:attribute name="about">
		  		<xsl:value-of select="metadata[@key='sampleid']/@value"/>
		    </xsl:attribute>
		    <dc:contributor>
		      <xsl:attribute name="resource"><xsl:value-of select="metadata[@key='sampleid']/@value"/><xsl:value-of select="metadata[@key='table_author_name']/@value"/></xsl:attribute>
		    </dc:contributor>
		    <xsl:apply-templates/>
		  </rdf:Description>
		  
		  <rdf:Description>
		    <xsl:attribute name="about">
		      <xsl:value-of select="metadata[@key='sampleid']/@value"/><xsl:value-of select="metadata[@key='table_author_name']/@value"/>
		    </xsl:attribute>
		    <rdf:type resource="foaf:Person"/>
		    <foaf:name><xsl:value-of select="metadata[@key='table_author_name']/@value"/></foaf:name>
		    <xsl:apply-templates mode="author"/>
		  </rdf:Description>
		</rdf:RDF>
	</xsl:template>
	
	<!-- general rule for translating properties -->
	<xsl:template match="metadata"> 
	  <xsl:element name="{@key}">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>
	
	<!-- in normal mode, don't do any author tags -->
	<xsl:template match="metadata[@key='table_author_abode'] | metadata[@key='table_author_age']">
	</xsl:template>
		
	<xsl:template match="metadata[@key='sampleid']"> 
	  <xsl:element name="dc:identifier">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>
	
	<xsl:template match="metadata[@key='table_text_year_of_writing']"> 
	  <xsl:element name="dc:date">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>
	
	<xsl:template match="metadata[@key='table_source']"> 
	  <xsl:element name="dc:source">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>

	<xsl:template match="metadata[@key='table_pages']"> 
	  <xsl:element name="dc:source">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>

  <!-- author mode rules -->
	<xsl:template mode="author" match="metadata[@key='table_author_abode']"> 
	  <xsl:element name="abode">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>

	<xsl:template mode="author" match="metadata[@key='table_author_age']"> 
	  <xsl:element name="age">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>

	<xsl:template mode="author" match="metadata[@key='table_author_abode']"> 
	  <xsl:element name="abode">
	    <xsl:value-of select="@value"/>
	  </xsl:element>
	</xsl:template>

</xsl:stylesheet>