from periods import periods
from dataclasses import dataclass, field
from entities import Author

authors = {
    "Pablo Picasso": Author(
        author_id=0,
        author_name="Pablo Picasso",
        # Historically associated primarily with Cubism(17) and also involved in Surrealism(18).
        main_periods=[periods[16], periods[17]],  # Cubism is period_id=17 (index 16), Surrealism=18 (index 17)
        # Key influences and contemporaries in Cubism include Georges Braque and Juan Gris.
        similar_authors=["Georges Braque", "Juan Gris"]
    ),
    "China": Author(
        author_id=1,
        author_name="China",
        # "China" is ambiguous as an author, but let's associate it with more contemporary periods,
        # reflecting global modern influences.
        # Choose: Contemporary Art(21) and Pop Art(20) as symbolic of broad modern cultural exchange.
        main_periods=[periods[20], periods[19]],  # Contemporary Art=21(index20), Pop Art=20(index19)
        # Similar authors as other culturally broad named entities, choosing "Japan" and "India" from the list.
        similar_authors=["Japan", "India"]
    ),
    "Georgia O'Keeffe": Author(
        author_id=2,
        author_name="Georgia O'Keeffe",
        # Known for pioneering American modernism, often associated with abstraction and certain mystical qualities.
        # Expressionism(16) and Surrealism(18) capture aspects of her style and era.
        main_periods=[periods[15], periods[17]],  # Expressionism=16(index15), Surrealism=18(index17)
        # Similar American modernists or related figures: Diego Rivera and Jasper Johns (both modern era).
        similar_authors=["Diego Rivera", "Jasper Johns"]
    ),
    "Claude Monet": Author(
        author_id=3,
        author_name="Claude Monet",
        # A leading figure in Impressionism(14), emerged from Realism(13).
        main_periods=[periods[12], periods[13]],  # Realism=13(index12), Impressionism=14(index13)
        # Similar authors: Édouard Manet and Pierre-Auguste Renoir were closely linked with Monet.
        similar_authors=["Édouard Manet", "Pierre-Auguste Renoir"]
    ),
    "Giovanni Battista": Author(
        author_id=4,
        author_name="Giovanni Battista",
        # Likely referring to Giovanni Battista Tiepolo, associated with Rococo(10) and late Baroque styles.
        main_periods=[periods[9], periods[8]],  # Rococo=10(index9), High Baroque=9(index8)
        # Similar authors: Jean-Honoré Fragonard and Jean-Antoine Watteau were prominent Rococo painters.
        similar_authors=["Jean-Honoré Fragonard", "Jean-Antoine Watteau"]
    ),
    "James McNeill": Author(
        author_id=5,
        author_name="James McNeill",
        # Referring to James McNeill Whistler, who moved from Realism(13) towards Impressionist influences(14).
        main_periods=[periods[12], periods[13]],  # Realism=13(index12), Impressionism=14(index13)
        # Similar authors: Edgar Degas and Édouard Manet also navigated between Realism and Impressionism.
        similar_authors=["Edgar Degas", "Édouard Manet"]
    ),
    "Japan": Author(
        author_id=6,
        author_name="Japan",
        # Japanese art influenced Impressionism(14) and Post-Impressionism(15).
        main_periods=[periods[13], periods[14]],  # Impressionism=14(index13), Post-Impressionism=15(index14)
        # Similar authors: "China" and "Vincent van" (Vincent van Gogh was influenced by Japanese prints)
        similar_authors=["China", "Vincent van"]
    ),
    "Edgar Degas": Author(
        author_id=7,
        author_name="Edgar Degas",
        # Degas was a leading Impressionist(14), also influenced by Realism(13).
        main_periods=[periods[12], periods[13]], # Realism=13(index12), Impressionism=14(index13)
        # Similar authors: Édouard Manet, Claude Monet were contemporaries in Impressionism.
        similar_authors=["Édouard Manet", "Claude Monet"]
    ),
    "Édouard Manet": Author(
        author_id=8,
        author_name="Édouard Manet",
        # Bridged Realism(13) and Impressionism(14).
        main_periods=[periods[12], periods[13]], # Realism=13(index12), Impressionism=14(index13)
        # Similar authors: Claude Monet, Edgar Degas
        similar_authors=["Claude Monet", "Edgar Degas"]
    ),
    "Paul Cezanne": Author(
        author_id=9,
        author_name="Paul Cezanne",
        # Cezanne was a central figure in Post-Impressionism(15), and emerged from Impressionism(14).
        main_periods=[periods[14], periods[13]], # Post-Impressionism=15(index14), Impressionism=14(index13)
        # Similar authors: "Vincent van" (Vincent van Gogh) and "Paul Gauguin" were key Post-Impressionists.
        similar_authors=["Vincent van", "Paul Gauguin"]
    ),
    "Marc Chagall": Author(
        author_id=10,
        author_name="Marc Chagall",
        # Associated with Expressionism(16) and Surrealism(18).
        main_periods=[periods[15], periods[17]], # Expressionism=16(index15), Surrealism=18(index17)
        # Similar authors: "Pablo Picasso" and "Vasily Kandinsky" (both key modernists/Expressionist influences).
        similar_authors=["Pablo Picasso", "Vasily Kandinsky"]
    ),
    "Roy Lichtenstein": Author(
        author_id=11,
        author_name="Roy Lichtenstein",
        # Known for Pop Art, also influenced by Abstract Expressionism
        main_periods=[periods[19], periods[20]],  # Abstract Expressionism(19)->index18, Pop Art(20)->index19
        similar_authors=["Andy Warhol", "Jasper Johns"]
    ),
    "Henri Matisse": Author(
        author_id=12,
        author_name="Henri Matisse",
        # Key figure in modern art, associated with Post-Impressionism, Impressionism influence, and Expressionism elements
        main_periods=[periods[14], periods[13], periods[15]],  
        # Impressionism(14)->index13, Realism(13)->index12 (for influence), Post-Impressionism(15)->index14, Expressionism(16)->index15
        # Similar modernists: Pablo Picasso (Cubism) and Marc Chagall (Expressionism/Surrealism)
        similar_authors=["Pablo Picasso", "Marc Chagall"]
    ),
    "Jasper Johns": Author(
        author_id=13,
        author_name="Jasper Johns",
        # Associated with Abstract Expressionism and a forerunner of Pop Art
        main_periods=[periods[18], periods[19]],  
        # Abstract Expressionism(19)->index18, Pop Art(20)->index19 but we already used 19 for Roy.
        # Let's keep as intended: Abstract Expressionism(19)=index18, Pop Art(20)=index19
        similar_authors=["Robert Delaunay", "Andy Warhol"]
    ),
    "Frank Lloyd": Author(
        author_id=14,
        author_name="Frank Lloyd",
        # Assuming reference to Frank Lloyd Wright; modern/innovative design.  
        # No direct architectural period, but let's pick Contemporary Art(21) symbolically.
        main_periods=[periods[20]],  # Contemporary Art(21)->index20
        # Similar authors (modern context): Bruce Nauman (conceptual/installation), Georges Braque (modern art)
        similar_authors=["Bruce Nauman", "Georges Braque"]
    ),
    "Diego Rivera": Author(
        author_id=15,
        author_name="Diego Rivera",
        # Mexican muralist, influenced by Post-Impressionism and Surrealism as well
        main_periods=[periods[14], periods[17]],  
        # Post-Impressionism(15)=index14, Surrealism(18)=index17
        # Similar authors: Pablo Picasso (modern influence), Paul Gauguin (Post-Impressionism link)
        similar_authors=["Pablo Picasso", "Paul Gauguin"]
    ),
    "Artist unknown": Author(
        author_id=16,
        author_name="Artist unknown",
        # Arbitrary choice: Maybe a single ancient or early period, Romanesque for anonymity
        main_periods=[periods[0]],  # Romanesque(1)=index0
        # Similar authors: "Attributed to", "Design attributed" to reflect uncertain origins
        similar_authors=["Attributed to", "Design attributed"]
    ),
    "Pierre-Auguste Renoir": Author(
        author_id=17,
        author_name="Pierre-Auguste Renoir",
        # A leading Impressionist, also touched by Realism at the start
        main_periods=[periods[12], periods[13]],  
        # Realism(13)=index12, Impressionism(14)=index13
        # Similar authors: Claude Monet, Édouard Manet
        similar_authors=["Claude Monet", "Édouard Manet"]
    ),
    "Henri de": Author(
        author_id=18,
        author_name="Henri de",
        # Likely referring to Henri de Toulouse-Lautrec, associated with Post-Impressionism
        main_periods=[periods[14]],  # Post-Impressionism(15)=index14
        # Similar authors: Vincent van (Van Gogh), Paul Cezanne (both Post-Impressionists)
        similar_authors=["Vincent van", "Paul Cezanne"]
    ),
    "Francisco José": Author(
        author_id=19,
        author_name="Francisco José",
        # Possibly Francisco José de Goya, bridging Romanticism and Realism
        main_periods=[periods[11], periods[12]],  
        # Romanticism(12)=index11, Realism(13)=index12
        # Similar authors: Francis Bacon (intensity of emotion), Salvador Dalí (Spanish and bridging eras)
        similar_authors=["Francis Bacon", "Salvador Dalí"]
    ),
    "Arshile Gorky": Author(
        author_id=20,
        author_name="Arshile Gorky",
        # Influential in Surrealism and Abstract Expressionism
        main_periods=[periods[17], periods[18]],  
        # Surrealism(18)=index17, Abstract Expressionism(19)=index18
        # Similar authors: Willem de (Willem de Kooning presumably), Georges Braque (modernist link)
        similar_authors=["Willem de", "Georges Braque"]
    ),
    "Paul Gauguin": Author(
        author_id=21,
        author_name="Paul Gauguin",
        # Leading Post-Impressionist
        main_periods=[periods[14]],  # Post-Impressionism(15)=index14
        # Similar authors: Vincent van (Van Gogh), Paul Cezanne
        similar_authors=["Vincent van", "Paul Cezanne"]
    ),
    "India Tamil": Author(
        author_id=22,
        author_name="India Tamil",
        # Let's associate with Islamic Golden Age and Contemporary Art, showing historical to modern transition
        main_periods=[periods[2], periods[20]],  
        # Islamic Golden Age(3)=index2, Contemporary Art(21)=index20
        # Similar authors: "India", "China" (reflecting geographic/cultural naming)
        similar_authors=["India", "China"]
    ),
    "Winslow Homer": Author(
        author_id=23,
        author_name="Winslow Homer",
        # Known for his marine subjects and landscapes, straddling Realism and early Impressionism.
        main_periods=[periods[12], periods[13]],  # Realism(13)=index12, Impressionism(14)=index13
        # Similar authors: other landscape or natural scene painters like "John Constable", "George Inness", and maybe a key Impressionist "Pierre-Auguste Renoir".
        similar_authors=["John Constable", "George Inness", "Pierre-Auguste Renoir"]
    ),
    "Vincent van": Author(
        author_id=24,
        author_name="Vincent van",
        # Vincent van Gogh was a Post-Impressionist, also influenced by Impressionism.
        main_periods=[periods[13], periods[14]], # Impressionism(14)=index13, Post-Impressionism(15)=index14
        # Similar authors: Paul Gauguin, Paul Cezanne, Édouard Manet
        similar_authors=["Paul Gauguin", "Paul Cezanne", "Édouard Manet"]
    ),
    "Claude Lorrain": Author(
        author_id=25,
        author_name="Claude Lorrain",
        # A French painter of the Baroque era, associated often with classical landscapes (High Baroque).
        main_periods=[periods[7], periods[8]], # Early Baroque(8)=index7, High Baroque(9)=index8
        # Similar authors: "Nicolas Poussin" (another French Baroque painter), "Rembrandt van" (Dutch Golden Age, close in period)
        similar_authors=["Nicolas Poussin", "Rembrandt van"]
    ),
    "Andy Warhol": Author(
        author_id=26,
        author_name="Andy Warhol",
        # Foremost figure in Pop Art, also interacted with Abstract Expressionism.
        main_periods=[periods[18], periods[19]], # Abstract Expressionism(19)=index18, Pop Art(20)=index19
        # Similar authors: "Roy Lichtenstein", "Jasper Johns", "Robert Delaunay" (modern art connections)
        similar_authors=["Roy Lichtenstein", "Jasper Johns", "Robert Delaunay"]
    ),
    "India Rajasthan,": Author(
        author_id=27,
        author_name="India Rajasthan,",
        # Representing a cultural region, let's associate with Islamic Golden Age and Contemporary Art to show historical breadth.
        main_periods=[periods[2], periods[20]], # Islamic Golden Age(3)=index2, Contemporary Art(21)=index20
        # Similar authors: "India", "China", "Teotihuacan Teotihuacan," (other cultural/geographical names)
        similar_authors=["India", "China", "Teotihuacan Teotihuacan,"]
    ),
    "Jean-Honoré Fragonard": Author(
        author_id=28,
        author_name="Jean-Honoré Fragonard",
        # A leading figure of the Rococo period.
        main_periods=[periods[9]], # Rococo(10)=index9
        # Similar authors: "Jean-Antoine Watteau" (Rococo), "Giovanni Battista" (Tiepolo, Rococo frescoes)
        similar_authors=["Jean-Antoine Watteau", "Giovanni Battista"]
    ),
    "George Inness": Author(
        author_id=29,
        author_name="George Inness",
        # An American landscape painter often associated with the transition from the Hudson River School (akin to Romanticism) to a more tonal, Realist approach.
        main_periods=[periods[11], periods[12]], # Romanticism(12)=index11, Realism(13)=index12
        # Similar authors: "Winslow Homer" (American landscape), "John Constable" (landscape tradition)
        similar_authors=["Winslow Homer", "John Constable"]
    ),
    "Korea": Author(
        author_id=30,
        author_name="Korea",
        # Cultural entity, let's pick Early Baroque and Contemporary Art arbitrarily.
        main_periods=[periods[7], periods[20]], # Early Baroque(8)=index7, Contemporary Art(21)=index20
        # Similar authors: "China", "Japan", "India" (other geographic/cultural names)
        similar_authors=["China", "Japan", "India"]
    ),
    "Willem de": Author(
        author_id=31,
        author_name="Willem de",
        # Likely Willem de Kooning, linked with Abstract Expressionism and also Surrealist influences.
        main_periods=[periods[17], periods[18]], # Surrealism(18)=index17, Abstract Expressionism(19)=index18
        # Similar authors: "Arshile Gorky" (AbEx), "Francis Bacon" (intense modern expression)
        similar_authors=["Arshile Gorky", "Francis Bacon"]
    ),
    "Eugène Delacroix": Author(
        author_id=32,
        author_name="Eugène Delacroix",
        # A French Romantic painter, also influenced by Neoclassicism.
        main_periods=[periods[10], periods[11]], # Neoclassicism(11)=index10, Romanticism(12)=index11
        # Similar authors: "Francisco José" (Goya), "Jacques-Louis David" (Neoclassical), "Gustave Moreau" (French painter influenced by Romanticism/Symbolism)
        similar_authors=["Francisco José", "Jacques-Louis David", "Gustave Moreau"]
    ),
    "Fernand Léger": Author(
        author_id=33,
        author_name="Fernand Léger",
        # A French modernist painter, associated with Cubism and also influenced by Surrealism.
        main_periods=[periods[16], periods[17]], # Cubism(17)=index16, Surrealism(18)=index17
        # Similar authors: "Pablo Picasso", "Georges Braque", "Juan Gris" (all Cubists)
        similar_authors=["Pablo Picasso", "Georges Braque", "Juan Gris"]
    ),
        "After a": Author(
        author_id=34,
        author_name="After a",
        # "After a" suggests works done after another artist or style. Let's assign Early Renaissance (a reference to older styles) and Contemporary Art (as a nod to reinterpretation).
        main_periods=[periods[4], periods[20]],  # Early Renaissance(5)=index4, Contemporary Art(21)=index20
        # Similar authors: "Artist unknown", "Design attributed", "Attributed to" since these also suggest uncertain or derivative provenance.
        similar_authors=["Artist unknown", "Design attributed", "Attributed to"]
    ),
    "Ivan Albright": Author(
        author_id=35,
        author_name="Ivan Albright",
        # American painter known for grotesque and detailed realism, so Realism and maybe Expressionism.
        main_periods=[periods[12], periods[15]], # Realism(13)=index12, Expressionism(16)=index15
        # Similar authors: "Francis Bacon" (known for intense expressionistic realism), "Edward Munch" (Expressionism)
        similar_authors=["Francis Bacon", "Edvard Munch"]
    ),
    "Spanish": Author(
        author_id=36,
        author_name="Spanish",
        # Represents a cultural/geographical entity. Let's assign Mannerism(7) and Baroque(9) reflecting the Golden Age of Spanish art.
        main_periods=[periods[6], periods[8]], # Mannerism(7)=index6, High Baroque(9)=index8
        # Similar authors: "Italian" styles not listed but we have "Giovanni Battista" (Italian), "Francisco José" (Goya, Spanish)
        # "Salvador Dalí" (Spanish Surrealist)
        similar_authors=["Francisco José", "Salvador Dalí", "Giovanni Battista"]
    ),
    "Rembrandt van": Author(
        author_id=37,
        author_name="Rembrandt van",
        # Rembrandt van Rijn, Dutch Golden Age, often linked to Baroque.
        main_periods=[periods[7], periods[8]], # Early Baroque(8)=index7, High Baroque(9)=index8
        # Similar authors: "Claude Lorrain" (Baroque era), "Nicolas Poussin" (Baroque)
        similar_authors=["Claude Lorrain", "Nicolas Poussin"]
    ),
    "Frederic Remington": Author(
        author_id=38,
        author_name="Frederic Remington",
        # American artist known for Western scenes; realistically capturing landscapes and battles might align with Realism and perhaps Romantic undertones.
        main_periods=[periods[11], periods[12]], # Romanticism(12)=index11, Realism(13)=index12
        # Similar authors: "Winslow Homer" (American realism), "George Inness" (American landscapes)
        similar_authors=["Winslow Homer", "George Inness"]
    ),
    "Design attributed": Author(
        author_id=39,
        author_name="Design attributed",
        # Suggests an uncertain origin, choose something broad like Gothic(2) and Contemporary(21) to show a wide span.
        main_periods=[periods[1], periods[20]], # Gothic(2)=index1, Contemporary Art(21)=index20
        # Similar authors: "Artist unknown", "Attributed to", "After a"
        similar_authors=["Artist unknown", "Attributed to", "After a"]
    ),
    "Attributed to": Author(
        author_id=40,
        author_name="Attributed to",
        # Similar reasoning: assign something like Proto-Renaissance(4) and Surrealism(18) for historical range.
        main_periods=[periods[3], periods[17]], # Proto-Renaissance(4)=index3, Surrealism(18)=index17
        # Similar authors: "Artist unknown", "Design attributed", "After a"
        similar_authors=["Artist unknown", "Design attributed", "After a"]
    ),
    "Georges Braque": Author(
        author_id=41,
        author_name="Georges Braque",
        # Co-founder of Cubism with Picasso, also had ties to Fauvism and Surrealism.
        main_periods=[periods[16], periods[17]], # Cubism(17)=index16, Surrealism(18)=index17
        # Similar authors: "Pablo Picasso", "Juan Gris", "Fernand Léger"
        similar_authors=["Pablo Picasso", "Juan Gris", "Fernand Léger"]
    ),
    "Vija Celmins": Author(
        author_id=42,
        author_name="Vija Celmins",
        # Known for photorealistic drawings and paintings of nature; associated with Realism revival and perhaps Contemporary art.
        main_periods=[periods[12], periods[20]], # Realism(13)=index12, Contemporary Art(21)=index20
        # Similar authors: "Bruce Nauman" (contemporary), "Georgia O'Keeffe" (nature-focused modernism), "Zao Wou-Ki" (modern landscapes)
        similar_authors=["Bruce Nauman", "Georgia O'Keeffe", "Zao Wou-Ki"]
    ),
    "Bruce Nauman": Author(
        author_id=43,
        author_name="Bruce Nauman",
        # Contemporary American artist known for conceptual and performance art; link to Abstract Expressionism, Surrealism, and Contemporary.
        main_periods=[periods[17], periods[20]], # Surrealism(18)=index17, Contemporary Art(21)=index20
        # Similar authors: "Jasper Johns" (modern American art), "Andy Warhol" (Pop/Conceptual), "Vija Celmins"
        similar_authors=["Jasper Johns", "Andy Warhol", "Vija Celmins"]
    ),
    "Meissen Porcelain": Author(
        author_id=44,
        author_name="Meissen Porcelain",
        # Not a painter, but a famous porcelain manufactory. Let's link it to Rococo (when it flourished) and also some earlier period for historical depth.
        main_periods=[periods[9], periods[1]], # Rococo(10)=index9, Gothic(2)=index1 to show old craftsmanship
        # Similar authors: "China" (porcelain origin), "Japan" (ceramic tradition), "India Rajasthan," (cultural art)
        similar_authors=["China", "Japan", "India Rajasthan,"]
    ),
    "Salvador Dalí": Author(
        author_id=45,
        author_name="Salvador Dalí",
        # Prominent Surrealist, also influenced by Cubism early on.
        main_periods=[periods[17], periods[18]], # Cubism(17)=index16, Surrealism(18)=index17
        # Similar authors: "Pablo Picasso" (Cubism), "René Magritte" (Surrealism), "Joan Miró" (not in the list, but we can pick "Arshile Gorky" as another surreal/abstract figure)
        similar_authors=["Pablo Picasso", "René Magritte", "Arshile Gorky"]
    ),
        "Edvard Munch": Author(
        author_id=46,
        author_name="Edvard Munch",
        # A pioneer of Expressionism, also influenced by Symbolism and Post-Impressionism.
        # Let's associate him with Expressionism(16) and a hint of Surrealism(18) for his mystical emotional landscapes.
        main_periods=[periods[15], periods[17]],  # Expressionism(16)=index15, Surrealism(18)=index17
        # Similar authors: "Vincent van" (Van Gogh, emotional intensity), "Francis Bacon" (modern expressionistic),
        # "Gustave Moreau" (symbolist influence), choose two for clarity:
        similar_authors=["Vincent van", "Francis Bacon"]
    ),
    "Emma Stebbins": Author(
        author_id=47,
        author_name="Emma Stebbins",
        # American sculptor of the mid-19th century, active during the Romantic and Realist transition.
        main_periods=[periods[11], periods[12]], # Neoclassicism(11)=index10 or Romanticism(12)=index11, Realism(13)=index12
        # Actually let's pick Romanticism(12) and Realism(13) due to the 19th century timeframe.
        # Similar authors (19th century, American/European): "Winslow Homer" (American), "George Inness" (American), "Frederic Remington" (American)
        similar_authors=["Winslow Homer", "George Inness", "Frederic Remington"]
    ),
    "Rudolph Schindler": Author(
        author_id=48,
        author_name="Rudolph Schindler",
        # R.M. Schindler was an early modern architect, 20th century, aligning with modern and contemporary art aesthetics.
        main_periods=[periods[20]], # Contemporary Art(21)=index20 for the modern era
        # Similar authors: "Frank Lloyd" (Wright), a modern architect, "Bruce Nauman" (contemporary), "Vija Celmins" (modern, contemporary)
        similar_authors=["Frank Lloyd", "Bruce Nauman"]
    ),
    "Meindert Hobbema": Author(
        author_id=49,
        author_name="Meindert Hobbema",
        # Dutch landscape painter of the 17th century, aligning with Baroque periods.
        main_periods=[periods[7], periods[8]], # Early Baroque(8)=index7, High Baroque(9)=index8
        # Similar authors: "Claude Lorrain" (landscape painter), "John Constable" (landscape painter), "Jan Sanders" (if we consider a historical painter)
        similar_authors=["Claude Lorrain", "John Constable"]
    ),
    "Stuart Davis": Author(
        author_id=50,
        author_name="Stuart Davis",
        # An American modernist painter influenced by Cubism and early American abstraction.
        main_periods=[periods[16], periods[18]], # Cubism(17)=index16, Surrealism(18)=index17 or Abstract Expressionism(19)=index18
        # Let's choose Cubism and Abstract Expressionism for a modernist link.
        # Similar authors: "Jasper Johns" (American modern), "Georgia O'Keeffe" (American modernist), "Robert Delaunay" (European abstract/cubist)
        similar_authors=["Jasper Johns", "Georgia O'Keeffe", "Robert Delaunay"]
    ),
    "Gustave Courbet": Author(
        author_id=51,
        author_name="Gustave Courbet",
        # Leader of the Realist movement in 19th century France.
        main_periods=[periods[12]], # Realism(13)=index12 (We can include just Realism)
        # Actually Romanticism(12)=index11 preceded Realism, Courbet was strongly Realist, let's add Realism only to emphasize.
        # Similar authors: "Édouard Manet" (transition from Realism to Impressionism), "Edgar Degas" (Impressionist with Realist roots),
        # "Jean-Honoré Fragonard" doesn't fit well timeframe-wise. Let's pick "Édouard Manet", "Edgar Degas", "Francisco José" (Goya, a precursor)
        similar_authors=["Édouard Manet", "Edgar Degas", "Francisco José"]
    ),
    "Jan Sanders": Author(
        author_id=52,
        author_name="Jan Sanders",
        # Possibly a Flemish or Dutch painter from Renaissance/Mannerist era.
        # Let's associate with Early Renaissance(5) and Mannerism(7) to reflect a transitional style.
        main_periods=[periods[4], periods[6]], # Early Renaissance(5)=index4, Mannerism(7)=index6
        # Similar authors: "Giovanni Battista" (Rococo/Baroque), "Lorenzo Monaco" (Early Renaissance), "Rogier van" (Early Netherlandish?)
        similar_authors=["Lorenzo Monaco", "Giovanni Battista", "Rogier van"]
    ),
    "John Constable": Author(
        author_id=53,
        author_name="John Constable",
        # English Romantic landscape painter.
        main_periods=[periods[11]], # Romanticism(12)=index11
        # Could also include Realism because of his detailed landscapes, but let's stick to Romanticism.
        # Similar authors: "George Inness", "Winslow Homer" (both landscape), "Claude Lorrain" (landscape tradition)
        similar_authors=["George Inness", "Winslow Homer", "Claude Lorrain"]
    ),
    "Sir Thomas": Author(
        author_id=54,
        author_name="Sir Thomas",
        # Possibly Sir Thomas Lawrence, English portrait painter in the late 18th-early 19th century.
        # Associated with Neoclassicism(11) and Romanticism(12).
        main_periods=[periods[10], periods[11]], # Rococo(10)=index9 or Neoclassicism(11)=index10 actually 0-based: Neoclassicism(11)=index10, Romanticism(12)=index11
        # Let's pick Neoclassicism and Romanticism.
        # Similar authors: "Thomas Eakins" (19th century portrait), "Pierre-Auguste Renoir" (19th century European), "Jacques-Louis David" (Neoclassical)
        similar_authors=["Thomas Eakins", "Jacques-Louis David", "Pierre-Auguste Renoir"]
    ),
    "Sir Joshua": Author(
        author_id=55,
        author_name="Sir Joshua",
        # Sir Joshua Reynolds, English 18th-century portrait painter, associated with the Grand Style in painting,
        # bridging between Rococo(10) and Neoclassicism(11).
        main_periods=[periods[9], periods[10]], # Rococo(10)=index9, Neoclassicism(11)=index10
        # Similar authors: "Jean-Honoré Fragonard" (Rococo), "Jacques-Louis David" (Neoclassicism), "Francisco José" (Goya, transitional)
        similar_authors=["Jean-Honoré Fragonard", "Jacques-Louis David", "Francisco José"]
    ),
    "Joseph Mallord": Author(
        author_id=56,
        author_name="Joseph Mallord",
        # Joseph Mallord William Turner, English Romantic painter.
        main_periods=[periods[11]], # Romanticism(12)=index11
        # Similar authors: "John Constable", "George Inness", "Winslow Homer" (all known for landscapes, emotional depth)
        similar_authors=["John Constable", "George Inness", "Winslow Homer"]
    ),
    "Francis Bacon": Author(
        author_id=57,
        author_name="Francis Bacon",
        # Irish-born British figurative painter known for his raw, emotive style: Expressionism(16), and some Surrealist undertones.
        main_periods=[periods[15], periods[17]], # Expressionism(16)=index15, Surrealism(18)=index17
        # Similar authors: "Edvard Munch" (Expressionist), "Arshile Gorky" (Abstract/Surreal), "Pablo Picasso" (Modern)
        similar_authors=["Edvard Munch", "Arshile Gorky", "Pablo Picasso"]
    ),
    "Nicolas Poussin": Author(
        author_id=58,
        author_name="Nicolas Poussin",
        # Baroque-era French painter, associated with Classical Baroque and influences of Neoclassicism.
        main_periods=[periods[8], periods[10]], # High Baroque(9)=index8, Neoclassicism(11)=index10
        # Similar authors: "Claude Lorrain" (French Baroque landscape), "Eugène Delacroix" (French tradition), "Jean-Honoré Fragonard" (French)
        similar_authors=["Claude Lorrain", "Eugène Delacroix", "Jean-Honoré Fragonard"]
    ),
    "Grant Wood": Author(
        author_id=59,
        author_name="Grant Wood",
        # American Regionalist painter, early 20th century, leaning towards a form of modern Realism and sometimes Folk influences.
        main_periods=[periods[12], periods[20]], # Realism(13)=index12, Contemporary Art(21)=index20 (to show a modern American context)
        # Similar authors: "Winslow Homer" (American realism), "Thomas Eakins" (American realism), "Georgia O'Keeffe" (American modern)
        similar_authors=["Winslow Homer", "Thomas Eakins", "Georgia O'Keeffe"]
    ),
    "Juan Gris": Author(
        author_id=60,
        author_name="Juan Gris",
        # One of the pioneers of Cubism.
        main_periods=[periods[16]], # Cubism(17)=index16
        # Similar authors: "Pablo Picasso", "Georges Braque", "Fernand Léger"
        similar_authors=["Pablo Picasso", "Georges Braque", "Fernand Léger"]
    ),
    "Vasily Kandinsky": Author(
        author_id=61,
        author_name="Vasily Kandinsky",
        # A pioneer of abstract art, associated with Expressionism and also influenced by The Blue Rider movement.
        main_periods=[periods[15], periods[19]], 
        # Expressionism(16)=index15, also Abstract Expressionism(19)=index18 could fit, or Surrealism(18)=index17 for abstraction.
        # Let's choose Expressionism(16)=index15 and Abstract Expressionism(19)=index18 for a nod to abstract progression.
        # Similar authors: "Robert Delaunay" (abstraction), "Marc Chagall" (modern, somewhat expressionistic), "Piet Mondrian" (not in list, choose "Pablo Picasso")
        similar_authors=["Robert Delaunay", "Marc Chagall", "Pablo Picasso"]
    ),
    "Émilie Charmy": Author(
        author_id=62,
        author_name="Émilie Charmy",
        # A French modernist painter, associated with Fauvism and Post-Impressionism trends.
        main_periods=[periods[14], periods[15]], # Impressionism(14)=index13, Post-Impressionism(15)=index14
        # Similar authors: "Henri Matisse" (Fauvism), "Paul Gauguin" (Post-Impressionism), "Vincent van" (Van Gogh)
        similar_authors=["Henri Matisse", "Paul Gauguin", "Vincent van"]
    ),
    "Robert Delaunay": Author(
        author_id=63,
        author_name="Robert Delaunay",
        # A key figure in Orphism (offshoot of Cubism), so Cubism and maybe Expressionism or Abstract Expressionism for modern abstraction.
        main_periods=[periods[16], periods[18]], # Cubism(17)=index16, Abstract Expressionism(19)=index18
        # Similar authors: "Vasily Kandinsky", "Fernand Léger", "Pablo Picasso"
        similar_authors=["Vasily Kandinsky", "Fernand Léger", "Pablo Picasso"]
    ),
    "Auguste Rodin": Author(
        author_id=64,
        author_name="Auguste Rodin",
        # French sculptor, late 19th to early 20th century, bridging Realism and Impressionism in sculpture.
        main_periods=[periods[12], periods[13], periods[14]], # Romanticism(12)=index11, Realism(13)=index12, Impressionism(14)=index13
        # Actually Rodin is mainly considered Realist with Symbolist influence. Let's choose Realism and Impressionism.
        # Similar authors: "Claude Monet" (Impressionist), "Édouard Manet" (Realist/Impressionist), "Edgar Degas" (Impressionist)
        similar_authors=["Claude Monet", "Édouard Manet", "Edgar Degas"]
    ),
    "Hermann Dudley": Author(
        author_id=65,
        author_name="Hermann Dudley",
        # Not a well-known figure; let's assume early 20th century American/European painter, maybe Expressionism or Post-Impressionism.
        main_periods=[periods[14], periods[15]], # Impressionism and Post-Impressionism
        # Similar authors: "Henri Matisse" (Post-Impressionism influence), "Berthe Morisot" (Impressionist), "Jasper Johns" (modern American)
        similar_authors=["Henri Matisse", "Berthe Morisot", "Jasper Johns"]
    ),
    "Guido Reni": Author(
        author_id=66,
        author_name="Guido Reni",
        # Italian Baroque painter.
        main_periods=[periods[7], periods[8]], # Early Baroque(8)=index7, High Baroque(9)=index8
        # Similar authors: "Rembrandt van" (Baroque), "Nicolas Poussin" (Baroque/Classicism), "Giovanni Battista" (Baroque/Rococo)
        similar_authors=["Rembrandt van", "Nicolas Poussin", "Giovanni Battista"]
    ),
    "Berthe Morisot": Author(
        author_id=67,
        author_name="Berthe Morisot",
        # A key female Impressionist painter.
        main_periods=[periods[13]], # Impressionism(14)=index13
        # Similar authors: "Claude Monet", "Pierre-Auguste Renoir", "Edgar Degas"
        similar_authors=["Claude Monet", "Pierre-Auguste Renoir", "Edgar Degas"]
    ),
    "India Andhra": Author(
        author_id=68,
        author_name="India Andhra",
        # Another culturally-named entry. Let's assign Islamic Golden Age and Contemporary to show a historical range.
        main_periods=[periods[2], periods[20]], # Islamic Golden Age(3)=index2, Contemporary Art(21)=index20
        # Similar authors: "India", "China", "Teotihuacan Teotihuacan," (geographic/cultural)
        similar_authors=["India", "China", "Teotihuacan Teotihuacan,"]
    ),
    "Teotihuacan Teotihuacan,": Author(
        author_id=69,
        author_name="Teotihuacan Teotihuacan,",
        # Ancient Mesoamerican city, let's assign Proto-Renaissance (mystical) and maybe Early Renaissance as symbolic.
        # Or Islamic Golden Age for a sense of ancient cultural flourishing. Actually, better to choose older periods:
        # Romanesque or Gothic won't match Mesoamerican culture historically, but we are free to choose.
        # Let's pick Romanesque for its antiquity sense and Contemporary for modern reinterpretations.
        main_periods=[periods[0], periods[20]], # Romanesque(1)=index0, Contemporary(21)=index20
        # Similar authors: "India Rajasthan,", "China", "Augsburg, Germany" (other geographic/cultural names)
        similar_authors=["India Rajasthan,", "Augsburg, Germany", "China"]
    ),
    "William Glackens": Author(
        author_id=70,
        author_name="William Glackens",
        # An American realist/impressionist painter of the Ashcan School, early 20th century.
        main_periods=[periods[12], periods[13], periods[14]], 
        # Romanticism(12)=index11 (a bit early), Realism(13)=index12, Impressionism(14)=index13. Let's focus on Realism and Impressionism:
        # Similar authors: "Winslow Homer" (American realism), "John Constable" (landscapes), "Robert Delaunay" (modern art influence)
        # Let's pick more consistent: "George Inness" (American landscapes), "Thomas Eakins" (American realism), "Grant Wood" (American)
        similar_authors=["George Inness", "Thomas Eakins", "Grant Wood"]
    ),
    "Bernat Martorell": Author(
        author_id=71,
        author_name="Bernat Martorell",
        # A Catalan painter from the Gothic/early Renaissance period.
        main_periods=[periods[1], periods[4]], # Gothic(2)=index1, Proto-Renaissance(4)=index3 or Early Renaissance(5)=index4
        # Let's choose Gothic and Early Renaissance.
        # Similar authors: "Giovanni di" (Early Italian?), "Lorenzo Monaco" (Early Renaissance), "Rogier van" (Early Netherlandish)
        similar_authors=["Giovanni di", "Lorenzo Monaco", "Rogier van"]
    ),
    "Zao Wou-Ki": Author(
        author_id=72,
        author_name="Zao Wou-Ki",
        # Chinese-French painter, associated with Abstraction, linked to Expressionism and sometimes Surrealism.
        main_periods=[periods[15], periods[17]], # Expressionism(16)=index15, Surrealism(18)=index17
        # Similar authors: "Vasily Kandinsky" (abstract), "Marc Chagall" (modernist), "Vija Celmins" (contemporary abstraction)
        similar_authors=["Vasily Kandinsky", "Marc Chagall", "Vija Celmins"]
    ),
    "Giovanni di": Author(
        author_id=73,
        author_name="Giovanni di",
        # Likely referring to an Early Renaissance Italian painter (e.g., Giovanni di Paolo).
        # Assign Gothic(2) and Early Renaissance(5).
        main_periods=[periods[1], periods[4]],  # Gothic(2)=index1, Early Renaissance(5)=index4
        # Similar authors: "Lorenzo Monaco", "Bernat Martorell", "Rogier van" (all early/gothic/renaissance)
        similar_authors=["Lorenzo Monaco", "Bernat Martorell", "Rogier van"]
    ),
    "Lorenzo Monaco": Author(
        author_id=74,
        author_name="Lorenzo Monaco",
        # Florentine painter transitioning from Gothic to Early Renaissance.
        main_periods=[periods[1], periods[4]], # Gothic(2)=index1, Early Renaissance(5)=index4
        # Similar authors: "Giovanni di", "Bernat Martorell", "Rogier van"
        similar_authors=["Giovanni di", "Bernat Martorell", "Rogier van"]
    ),
    "Rogier van": Author(
        author_id=75,
        author_name="Rogier van",
        # Rogier van der Weyden, Early Netherlandish painter, related to Gothic/Early Renaissance.
        main_periods=[periods[1], periods[4]], # Gothic and Early Renaissance
        # Similar authors: "Giovanni di", "Lorenzo Monaco", "Bernat Martorell"
        similar_authors=["Giovanni di", "Lorenzo Monaco", "Bernat Martorell"]
    ),
    "Jean Hey": Author(
        author_id=76,
        author_name="Jean Hey",
        # Master of Moulins, late 15th-century French painter, Gothic to Early Renaissance transition.
        main_periods=[periods[1], periods[4]],
        # Similar authors: "Rogier van" (Flemish), "Bernat Martorell", "Giovanni di"
        similar_authors=["Rogier van", "Bernat Martorell", "Giovanni di"]
    ),
    "Dante Gabriel": Author(
        author_id=77,
        author_name="Dante Gabriel",
        # Dante Gabriel Rossetti, Pre-Raphaelite, mid-late 19th century, influenced by Romanticism.
        main_periods=[periods[11], periods[12]], # Neoclassicism(11)=index10, Romanticism(12)=index11
        # Pre-Raphaelites took inspiration from medieval/early Renaissance but stylistically closer to Romanticism.
        # Let's pick Romanticism(12)=index11 and Realism(13)=index12, but Romanticism is key. We'll keep Romanticism alone or add Realism.
        # Actually, let's do Romanticism only for clarity.
        # Similar authors: "Eugène Delacroix" (Romantic), "Gustave Moreau" (Symbolist with Romantic streak), "Edvard Munch" (emotional intensity)
        similar_authors=["Eugène Delacroix", "Gustave Moreau", "Edvard Munch"]
    ),
    "Chimú North": Author(
        author_id=78,
        author_name="Chimú North",
        # Ancient Mesoamerican culture. Let's pick Romanesque(1) for antiquity and Islamic Golden Age(3) for historical richness.
        main_periods=[periods[0], periods[2]], # Romanesque(1)=index0, Islamic Golden Age(3)=index2
        # Similar authors: other culturally indicative names: "Teotihuacan Teotihuacan,", "Augsburg, Germany", "India Andhra"
        similar_authors=["Teotihuacan Teotihuacan,", "Augsburg, Germany", "India Andhra"]
    ),
    "Jean-Antoine Watteau": Author(
        author_id=79,
        author_name="Jean-Antoine Watteau",
        # A key Rococo painter.
        main_periods=[periods[9]], # Rococo(10)=index9
        # Similar authors: "Jean-Honoré Fragonard" (Rococo), "Giovanni Battista" (Tiepolo, Rococo frescoes), "Pierre-Auguste Renoir" (French tradition, though later)
        similar_authors=["Jean-Honoré Fragonard", "Giovanni Battista", "Pierre-Auguste Renoir"]
    ),
    "Gustave Moreau": Author(
        author_id=80,
        author_name="Gustave Moreau",
        # French Symbolist painter, late 19th century, influenced by Romanticism and Symbolism (close to Post-Impressionism era).
        main_periods=[periods[11], periods[14]], # Romanticism(12)=index11, Post-Impressionism(15)=index14
        # Similar authors: "Eugène Delacroix" (Romantic), "Dante Gabriel" (Pre-Raphaelite/Romantic), "Edvard Munch" (intense symbolic/expressive)
        similar_authors=["Eugène Delacroix", "Dante Gabriel", "Edvard Munch"]
    ),
    "Gustave Caillebotte": Author(
        author_id=81,
        author_name="Gustave Caillebotte",
        # French painter bridging Realism and Impressionism.
        main_periods=[periods[12], periods[13]], # Realism(13)=index12, Impressionism(14)=index13
        # Similar authors: "Claude Monet", "Edgar Degas", "Berthe Morisot"
        similar_authors=["Claude Monet", "Edgar Degas", "Berthe Morisot"]
    ),
    "Albrecht Dürer": Author(
        author_id=82,
        author_name="Albrecht Dürer",
        # German Renaissance, associated with High Renaissance ideals.
        main_periods=[periods[4], periods[5]], # Early Renaissance(5)=index4, High Renaissance(6)=index5
        # Similar authors: "Correggio (Antonio" (Italian High Renaissance), "Giovanni di" (Early Renaissance), "Lorenzo Monaco" (Early Renaissance)
        similar_authors=["Correggio (Antonio", "Giovanni di", "Lorenzo Monaco"]
    ),
    "Correggio (Antonio": Author(
        author_id=83,
        author_name="Correggio (Antonio",
        # Italian High Renaissance/Mannerist painter.
        main_periods=[periods[5], periods[6]], # High Renaissance(6)=index5, Mannerism(7)=index6
        # Similar authors: "Albrecht Dürer" (Renaissance), "Giovanni Battista" (later Italian painter), "Jacques-Louis David" (Neoclassical, but admired Renaissance)
        similar_authors=["Albrecht Dürer", "Giovanni Battista", "Jacques-Louis David"]
    ),
    "German, Cologne": Author(
        author_id=84,
        author_name="German, Cologne",
        # Refers to a regional style, likely Gothic/Early Renaissance era in German lands.
        main_periods=[periods[1], periods[4]], # Gothic and Early Renaissance
        # Similar authors: "Bernat Martorell", "Giovanni di", "Rogier van"
        similar_authors=["Bernat Martorell", "Giovanni di", "Rogier van"]
    ),
    "Francesco Durantino": Author(
        author_id=85,
        author_name="Francesco Durantino",
        # Not widely known, but let's assume an Italian Renaissance painter.
        main_periods=[periods[4], periods[5]], # Early Renaissance and High Renaissance
        # Similar authors: "Lorenzo Monaco", "Bernat Martorell", "Correggio (Antonio"
        similar_authors=["Lorenzo Monaco", "Bernat Martorell", "Correggio (Antonio"]
    ),
    "Jacques-Louis David": Author(
        author_id=86,
        author_name="Jacques-Louis David",
        # Leading figure in Neoclassicism.
        main_periods=[periods[10]], # Neoclassicism(11)=index10
        # Similar authors: "Nicolas Poussin" (admired by Neoclassicists), "Sir Joshua" (English painter in Neoclassical era), "Eugène Delacroix" (next gen Romantic)
        similar_authors=["Nicolas Poussin", "Sir Joshua", "Eugène Delacroix"]
    ),
    "Peter Paul": Author(
        author_id=87,
        author_name="Peter Paul",
        # Peter Paul Rubens, Flemish Baroque painter.
        main_periods=[periods[7], periods[8]], # Early Baroque(8)=index7, High Baroque(9)=index8
        # Similar authors: "Rembrandt van" (Baroque), "Guido Reni" (Italian Baroque), "Giovanni Battista" (Baroque/Rococo)
        similar_authors=["Rembrandt van", "Guido Reni", "Giovanni Battista"]
    ),
        "Amedeo Modigliani": Author(
        author_id=88,
        author_name="Amedeo Modigliani",
        # Italian painter and sculptor associated with Modernism, influenced by Post-Impressionism and Expressionism.
        main_periods=[periods[14], periods[15]], # Impressionism(14)=index13, Post-Impressionism(15)=index14, Expressionism(16)=index15
        # Let's pick Post-Impressionism and Expressionism to capture his style.
        # Similar authors: "Pablo Picasso", "Henri Matisse", "Marc Chagall" (all modern masters)
        similar_authors=["Pablo Picasso", "Henri Matisse", "Marc Chagall"]
    ),
    "Georges Seurat": Author(
        author_id=89,
        author_name="Georges Seurat",
        # Pioneer of Pointillism/Divisionism, associated with Post-Impressionism.
        # He built upon Impressionism but moved into Post-Impressionism.
        main_periods=[periods[13], periods[14]], # Impressionism(14)=index13, Post-Impressionism(15)=index14
        similar_authors=["Paul Cezanne", "Vincent van", "Robert Delaunay"]
    ),
    "William Merritt": Author(
        author_id=90,
        author_name="William Merritt",
        # Likely William Merritt Chase, American Impressionist, also influenced by Realism.
        main_periods=[periods[12], periods[13]], # Realism(13)=index12, Impressionism(14)=index13
        similar_authors=["Winslow Homer", "John Constable", "Claude Monet"]
    ),
    "William Sidney": Author(
        author_id=91,
        author_name="William Sidney",
        # Possibly William Sidney Mount, American genre painter of the 19th century, linked to Realism, with some Romantic undertones.
        main_periods=[periods[11], periods[12]], # Neoclassicism(11)=index10, Romanticism(12)=index11, Realism(13)=index12
        # More appropriate would be Romanticism and Realism. Let's pick Romanticism(12)=index11 and Realism(13)=index12.
        similar_authors=["Winslow Homer", "George Inness", "Grant Wood"]
    ),
    "Giorgio de": Author(
        author_id=92,
        author_name="Giorgio de",
        # Giorgio de Chirico, known for Metaphysical art influencing Surrealism and Expressionism.
        main_periods=[periods[15], periods[17]], # Expressionism(16)=index15, Surrealism(18)=index17
        similar_authors=["René Magritte", "Salvador Dalí", "Pablo Picasso"]
    ),
    "Thomas Eakins": Author(
        author_id=93,
        author_name="Thomas Eakins",
        # American realist painter.
        main_periods=[periods[12]], # Realism(13)=index12
        similar_authors=["Winslow Homer", "George Inness", "Grant Wood"]
    ),
    "Augsburg, Germany": Author(
        author_id=94,
        author_name="Augsburg, Germany",
        # Cultural/geographical entry, choose early periods: Romanesque and Gothic.
        main_periods=[periods[0], periods[1]], # Romanesque(1)=index0, Gothic(2)=index1
        similar_authors=["Teotihuacan Teotihuacan,", "Chimú North", "India Andhra"]
    ),
    "René Magritte": Author(
        author_id=95,
        author_name="René Magritte",
        # Belgian Surrealist.
        main_periods=[periods[17]], # Surrealism(18)=index17
        # Similar authors: "Salvador Dalí" (Surrealist), "Giorgio de" (Metaphysical/Surreal), "Francis Bacon" (modern expressive)
        similar_authors=["Salvador Dalí", "Giorgio de", "Francis Bacon"]
    ),
    "India": Author(
        author_id=96,
        author_name="India",
        # Another cultural/geographical name.
        # Assign Islamic Golden Age and Contemporary Art.
        main_periods=[periods[2], periods[20]], # Islamic Golden Age(3)=index2, Contemporary(21)=index20
        similar_authors=["China", "Japan", "India Andhra"]
    ),
    "Huang Binhong": Author(
        author_id=97,
        author_name="Huang Binhong",
        # Chinese painter (20th century), known for landscapes, bridging traditional ink painting with modern sensibilities.
        # Possibly link to Expressionism and Contemporary Art.
        main_periods=[periods[15], periods[20]], # Expressionism(16)=index15, Contemporary(21)=index20
        # Similar authors: "Zao Wou-Ki" (Chinese modern painter), "Vija Celmins" (detailed landscapes), "Georgia O'Keeffe" (landscapes)
        similar_authors=["Zao Wou-Ki", "Vija Celmins", "Georgia O'Keeffe"]
    ),
    "Jim Nutt": Author(
        author_id=98,
        author_name="Jim Nutt",
        # American artist, Chicago Imagist (mid/late 20th century), influenced by Pop Art and Expressionistic tendencies.
        main_periods=[periods[15], periods[19], periods[20]], 
        # Expressionism(16)=index15, Abstract Expressionism(19)=index18, Pop Art(20)=index19. Let's pick two: Expressionism and Pop Art.
        # Similar authors: "Andy Warhol", "Roy Lichtenstein", "Jasper Johns" (Pop/modern American)
        similar_authors=["Andy Warhol", "Roy Lichtenstein", "Jasper Johns"]
    )
}